"""
build_index.py — corre en local, no requiere GPU.
Genera faiss.index, retrieval_index.json y los .pkl para Colab.
"""
import os, sys, json, re, unicodedata, time, warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTORCH_JIT"]            = "0"    # evita segfault en Mac Apple Silicon
os.environ["OMP_NUM_THREADS"]        = "1"    # single thread, más estable en Mac
warnings.filterwarnings("ignore")

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import faiss
import torch
torch.backends.mps.is_available = lambda: False   # forzar CPU puro en Mac
from pathlib import Path
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModel
from scripts.chunker import SentenceTextSplitter, load_markdown_as_pages

BASE   = Path(__file__).parent.parent
DATA   = BASE / "Data"
KB_DIR = DATA / "knowledge_base" / "knowledge_base"

RANDOM_STATE = 42
PROMPT_K     = 3

print("=" * 50)
print("ARTEMIS — build_index.py")
print("=" * 50)

# ── 1. Cargar y limpiar train/test ────────────────────────────────────────────
print("\n[1/5] Cargando datos...")
train_raw = pd.read_csv(DATA / "train.csv")
test_df   = pd.read_csv(DATA / "test.csv")

with open(DATA / "tools_definition.json") as f:
    tools_def_raw = json.load(f)
TOOLS_DEF   = {t["name"]: t for t in tools_def_raw["tools"]}
VALID_TOOLS = list(TOOLS_DEF.keys())

def extract_tool_name(tc): return tc.split("(")[0].strip()
def normalize_query(text):
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()

train_raw["tool_name"] = train_raw["tool_call"].apply(extract_tool_name)
df = train_raw.drop_duplicates(subset=["query"])
df = df[df["tool_name"].isin(VALID_TOOLS)].copy()
df["query"]      = df["query"].apply(normalize_query)
test_df["query"] = test_df["query"].apply(normalize_query)
print(f"  Dataset limpio: {len(df)} ejemplos")

train_df, val_df = train_test_split(
    df, test_size=0.10, random_state=RANDOM_STATE, stratify=df["tool_name"]
)
train_df = train_df.reset_index(drop=True)
val_df   = val_df.reset_index(drop=True)
print(f"  Train: {len(train_df)} | Val: {len(val_df)}")

# ── 2. Chunking ───────────────────────────────────────────────────────────────
print("\n[2/5] Chunking knowledge base...")
splitter = SentenceTextSplitter(section_length=800, overlap_pct=0.20, max_tokens=400)
chunks = []
for doc_path in sorted(KB_DIR.rglob("doc.md")):
    doc_id = doc_path.parent.name
    for i, sp in enumerate(splitter.split_pages(load_markdown_as_pages(str(doc_path)))):
        chunks.append({"doc_id": doc_id, "chunk_id": i, "text": sp.text})
print(f"  Chunks: {len(chunks)}")

# ── 3. Embedding con transformers (sin sentence_transformers) ─────────────────
print("\n[3/5] Embeddings con BAAI/bge-small-en-v1.5 (CPU)...")
_tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")
_model     = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5")
_model.eval()

def encode(texts, batch_size=32):
    all_vecs = []
    n = len(texts)
    for i in range(0, n, batch_size):
        batch = texts[i : i + batch_size]
        enc = _tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            out = _model(**enc)
        vecs = torch.nn.functional.normalize(out.last_hidden_state[:, 0, :], p=2, dim=1)
        all_vecs.append(vecs.cpu().numpy())
        done = min(i + batch_size, n)
        print(f"  {done}/{n} chunks embebidos", end="\r")
    print()
    return np.concatenate(all_vecs, axis=0)

t0   = time.time()
vecs = encode([c["text"] for c in chunks])
print(f"  Shape: {vecs.shape} | Tiempo: {time.time()-t0:.1f}s")

# ── 4. FAISS + retrieval_index.json ──────────────────────────────────────────
print("\n[4/5] Construyendo índice FAISS...")
index = faiss.IndexFlatIP(vecs.shape[1])
index.add(vecs.astype(np.float32))
faiss.write_index(index, str(BASE / "faiss.index"))
print(f"  {index.ntotal} vectores → faiss.index")

for i, c in enumerate(chunks):
    c["vector"] = vecs[i].tolist()
with open(BASE / "retrieval_index.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False)
print("  retrieval_index.json guardado")

# ── 5. Pre-recuperar contexto y exportar pkl ──────────────────────────────────
print("\n[5/5] Pre-recuperando contexto para train/val/test...")

def retrieve(query, k=PROMPT_K):
    q_enc = _tokenizer([query], padding=True, truncation=True, max_length=512, return_tensors="pt")
    with torch.no_grad():
        out = _model(**q_enc)
    q_vec = torch.nn.functional.normalize(out.last_hidden_state[:, 0, :], p=2, dim=1).cpu().numpy().astype(np.float32)
    _, idxs = index.search(q_vec, k)
    return [chunks[i] for i in idxs[0] if i < len(chunks)]

for name, split_df in [("train", train_df), ("val", val_df), ("test", test_df)]:
    print(f"  {name} ({len(split_df)} queries)...", end=" ", flush=True)
    split_df["context_chunks"] = split_df["query"].apply(retrieve)
    split_df.to_pickle(BASE / f"{name}_processed.pkl")
    print("OK")

print("\n" + "=" * 50)
print("LISTO. Archivos generados:")
for f in ["faiss.index", "retrieval_index.json",
          "train_processed.pkl", "val_processed.pkl", "test_processed.pkl"]:
    p = BASE / f
    size = p.stat().st_size / 1024 / 1024 if p.exists() else 0
    status = f"{size:.1f} MB" if p.exists() else "FALTA"
    print(f"  {f}: {status}")
print("=" * 50)
print("\nSigue en lora.ipynb en Colab.")
