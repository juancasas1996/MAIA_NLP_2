# ARTEMIS — CLAUDE.md (Exp_2: encoder fine-tuned)
## Competencia MAPL-202601 · Deadline 2026-05-24

**Experimento 2** — mismo sistema que Exp_1 (88% Kaggle) pero con el encoder **bge-small-en-v1.5 fine-tuneado** mediante TripletLoss sobre los 622 hard-negative triplets de `consultas_centro_control.json`. Objetivo: mejorar el retrieval P@K y con ello el exact match final.

---

## Diferencia respecto a Exp_1 (88143)

| | Exp_1 | Exp_2 |
|---|---|---|
| Encoder | bge-small base | bge-small **fine-tuned** |
| FAISS index | vectores originales | vectores del encoder fine-tuned |
| PKLs | generados con rag.ipynb | generados con **encoder_finetune.ipynb** |
| Score Kaggle | 88% | pendiente |

---

## Orden de ejecución

1. **`encoder_finetune.ipynb`** — Colab T4 (~30 min) — **PRIMERO**
   - Fine-tune encoder, rebuild FAISS, regenera PKLs, guarda todo en Drive
2. **`lora.ipynb`** — Colab A100/T4 (~2.5-7h) — SEGUNDO
   - Usa los PKLs generados por encoder_finetune.ipynb
3. Subir `submission.csv` a Kaggle

---

## Estructura de archivos

```
Exp_2_encoder_tuned/
├── CLAUDE.md                     ← este archivo
├── encoder_finetune.ipynb        ← CORRER PRIMERO (Colab T4) — fine-tune encoder + rebuild index
├── rag.ipynb                     ← referencia (NO necesario correr — encoder_finetune.ipynb lo reemplaza)
├── lora.ipynb                    ← CORRER SEGUNDO (Colab GPU) — LoRA fine-tuning
├── pipeline.ipynb                ← entregable obligatorio de la competencia (5 secciones)
├── requirements.txt              ← dependencias (local + Colab)
├── textsplitter.py               ← original de Microsoft Azure (referencia)
│
├── scripts/
│   ├── chunker.py                ← SentenceTextSplitter standalone
│   └── build_index.py            ← script alternativo
│
├── Data/ → symlink a ../Data/    ← mismos datos que Exp_1
│
└── (generados por encoder_finetune.ipynb tras correr en Colab):
    ├── encoder_finetuned/        ← modelo fine-tuned (guardar en Drive)
    ├── faiss.index               ← índice con vectores fine-tuned
    ├── retrieval_index.json      ← chunks + vectores fine-tuned — entregable
    ├── train_processed.pkl       ← 2,313 filas con context_chunks (encoder fine-tuned)
    ├── val_processed.pkl         ← 257 filas
    └── test_processed.pkl        ← 766 filas
```

---

## Herramientas disponibles (tools_definition.json)

Todos los parámetros son enums — no hay valores libres. El formato es **exacto**:
- Strings con comillas simples: `module='condor'`
- Enteros sin comillas: `timeframe_hours=6`
- Sin espacios: `func(a='x',b=6)` — NO `func(a='x', b=6)`
- Orden de parámetros fijo según `parameter_order`

| Tool | Parámetros |
|------|-----------|
| `get_telemetry` | `module`, `metric`, `timeframe_hours` |
| `get_crew_status` | `module`, `info` |
| `get_module_status` | `module`, `system` |
| `send_alert` | `module`, `severity`, `reason` |
| `send_message` | `recipient`, `priority` |
| `schedule_maintenance` | `module`, `task`, `priority` |
| `activate_protocol` | `protocol_id`, `scope` |
| `control_system` | `module`, `system`, `action` |
| `calculate_trajectory` | `maneuver`, `urgency` |
| `request_supply` | `category`, `urgency` |
| `no_action` | (sin parámetros) |

Valores clave:
- `module`: `condor`, `quetzal`, `jaguar`, `colibri`, `vicuna`, `tucan`
- `severity`: `low`, `medium`, `high`, `critical`
- `timeframe_hours`: `1`, `6`, `12`, `24` (integers)

---

## Modelos obligatorios

| Rol | Modelo | Configuración |
|-----|--------|--------------|
| Decoder (generación) | `meta-llama/Llama-3.2-1B-Instruct` | LoRA r=64, alpha=128, bfloat16 sin cuantizar |
| Encoder (retrieval) | `BAAI/bge-small-en-v1.5` | CPU, transformers directo (NO sentence_transformers en Mac) |

**Llama-3.2-1B-Instruct es GATED** — requiere token HF + aceptar licencia Meta en huggingface.co.

---

## Qué se ha hecho (estado actual)

### ✅ Completado

1. **`scripts/chunker.py`** — SentenceTextSplitter standalone extraído de textsplitter.py
   - Sin dependencias de Azure (`app.utils.settings`, `.page`)
   - Usa `tiktoken.get_encoding("cl100k_base")` en lugar de ada-002
   - `section_length=800`, `overlap=20%`, `max_tokens=400`
   - Genera 785 chunks desde los 54 docs de la KB

2. **`rag.ipynb`** — Pipeline RAG completo, corrido exitosamente en local
   - Apple Silicon fix: `PYTORCH_JIT=0`, `OMP_NUM_THREADS=1`, `torch.backends.mps.is_available = lambda: False`
   - Encoder via transformers directo (NO sentence_transformers — causa segfault en Mac)
   - FAISS IndexFlatIP (dot product sobre vectores normalizados = cosine)
   - **Hybrid search implementado**: BM25 + FAISS + Reciprocal Rank Fusion (RRF k=60)
   - Métricas dense puras: P@1=0.57, P@3=0.75, P@5=0.81, P@8=0.86
   - PKLs generados con hybrid search (PROMPT_K=3 chunks por ejemplo)

3. **`encoder_finetune.ipynb`** ← **NUEVO en Exp_2** — Colab T4, ~30 min:
   - Fine-tune bge-small-en-v1.5 con TripletLoss (622 hard-negative triplets)
   - Evalúa P@K baseline vs fine-tuned automáticamente
   - Rebuild FAISS con vectores fine-tuned
   - Regenera PKLs (train/val/test) con hybrid search
   - Guarda todo en Drive

4. **`lora.ipynb`** — notebook Colab con LoRA fine-tuning completo:
   - LoRA: r=64, alpha=128, dropout=0.05, todos los módulos (q/k/v/o + gate/up/down proj)
   - Solo entrena el tool_call (labels=-100 para prompt/contexto)
   - 8 épocas, batch=4, grad_accum=8 (efectivo=32), lr=2e-4, cosine scheduler
   - Early stopping patience=3

5. **`pipeline.ipynb`** — entregable de competencia (5 secciones requeridas)

6. **`requirements.txt`** — dependencias actualizadas con `rank-bm25`

### ⏳ Pendiente (Exp_2)

- [ ] **Subir a Drive** antes de encoder_finetune.ipynb:
  - `retrieval_index.json`, `Data/tools_definition.json`, `Data/consultas_centro_control.json`
  - `Data/train.csv`, `Data/test.csv`, `Data/knowledge_base/`
- [ ] **Correr `encoder_finetune.ipynb` en Colab T4** (~30 min)
- [ ] **Correr `lora.ipynb` en Colab** con GPU A100/T4 (~2.5-7h)
  - Los PKLs ya fueron generados por encoder_finetune.ipynb
  - Agregar HF token para Llama gateado
- [ ] **Generar `submission.csv`** desde `lora.ipynb`
- [ ] **Subir submission a Kaggle** y comparar con 88% de Exp_1
- [ ] **Guardar `decoder_checkpoint/`** — entregable obligatorio

---

## Cómo correr el proyecto

### Paso 1 — Encoder fine-tuning + rebuild index (Colab T4, ~30 min)

Subir a Drive (`/content/drive/MyDrive/MASTER/Tercer_semestre/NLP_2/Competencia/`):
- `retrieval_index.json` (del Exp_1)
- `Data/tools_definition.json`, `Data/consultas_centro_control.json`
- `Data/train.csv`, `Data/test.csv`, `Data/knowledge_base/`

Luego abrir `encoder_finetune.ipynb` en Colab T4 y correr todas las celdas.
El notebook genera y guarda en Drive: `encoder_finetuned/`, `faiss.index`, `retrieval_index.json`, `train_processed.pkl`, `val_processed.pkl`, `test_processed.pkl`.

### Paso 2 — LoRA fine-tuning (Colab A100/T4)

```python
# En lora.ipynb, celda 0:
DRIVE_PATH = "/content/drive/MyDrive/MASTER/Tercer_semestre/NLP_2/Competencia"

# Agregar HF token:
from huggingface_hub import login
login(token="hf_...")   # token de https://huggingface.co/settings/tokens
```

Los PKLs (train/val/test_processed.pkl) ya están en Drive tras el Paso 1.

Archivos adicionales en Drive antes de lora.ipynb:
- `train_processed.pkl`, `val_processed.pkl`, `test_processed.pkl`
- `retrieval_index.json`
- `Data/tools_definition.json`

### Paso 3 — Submission

```bash
# submission.csv se genera automáticamente al final de lora.ipynb
# Subir a Kaggle: https://www.kaggle.com/competitions/mapl-202601
```

---

## Detalles técnicos importantes

### Apple Silicon (Mac) — fix segfault

Siempre antes de importar torch:

```python
import os
os.environ["PYTORCH_JIT"]     = "0"
os.environ["OMP_NUM_THREADS"] = "1"
import torch
torch.backends.mps.is_available = lambda: False
```

O correr scripts con: `PYTORCH_JIT=0 OMP_NUM_THREADS=1 python script.py`

### Encoder — NO usar sentence_transformers en Mac

```python
# BIEN — transformers directo
from transformers import AutoTokenizer, AutoModel
_enc_tok = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")
_enc_mdl = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5")
_enc_mdl.eval()

# MAL en Mac — causa segfault (exit code 139)
# from sentence_transformers import SentenceTransformer
```

### Hybrid search — RRF

```python
# RRF score = Σ 1/(rrf_k + rank)   con rrf_k=60 (estándar)
# Combina FAISS dense (semántico) + BM25 (keyword/términos técnicos exactos)
# Mejora P@K ~+5-10% sobre solo dense, especialmente para IDs como MASA-SEC-012
```

### Formato del prompt (Llama-3.2-Instruct chat template)

```python
SYSTEM_PROMPT = """You are ARTEMIS, the AI control system for MASA's Kuntur Station.
Given an operator query and relevant documentation, output ONLY the exact tool call.

Format rules (STRICT — any deviation = wrong answer):
- No spaces after commas or around '=' signs
- Single quotes for string values: module='condor'
- Integer values without quotes: timeframe_hours=6
- Parameter ORDER must match the tool definition exactly
- Module names are lowercase ASCII: condor, quetzal, jaguar, colibri, vicuna, tucan
- Protocol IDs UPPERCASE: MASA-SEC-012
- For purely informational queries with no system action: no_action"""
```

### tools_definition.json — estructura real

```python
with open("Data/tools_definition.json") as f:
    tools_def_raw = json.load(f)
# Es {"tools": [lista de tools]}, NO un dict directo
TOOLS_DEF = {t["name"]: t for t in tools_def_raw["tools"]}
```

### Dataset tras limpieza

- Raw: 2,718 filas → 148 duplicados eliminados → 2,570 limpias
- Split: 2,313 train / 257 val (90/10, estratificado por tool_name)
- Test: 766 queries sin labels

---

## Entregables obligatorios de la competencia

| Entregable | Archivo | Estado |
|-----------|---------|--------|
| Índice de retrieval | `retrieval_index.json` | ✅ Generado |
| Checkpoint LoRA | `decoder_checkpoint/` | ⏳ Requiere Colab |
| Notebook principal | `pipeline.ipynb` | ✅ Creado |
| Predicciones | `submission.csv` | ⏳ Requiere Colab |

---

## Tiempos estimados

| Tarea | Dónde | Tiempo |
|-------|-------|--------|
| Correr hybrid search + regenerar PKLs | Local Mac | ~5-8 min |
| LoRA fine-tuning (8 épocas) | Colab A100 | ~2-2.5 h |
| LoRA fine-tuning (8 épocas) | Colab T4 | ~5-7 h |
| Inferencia test.csv (766 queries) | Colab GPU | ~5-10 min |

---

## Métricas actuales (dense-only, sin fine-tuning)

| k | P@k | R@k |
|---|-----|-----|
| 1 | 0.5704 | 0.5704 |
| 3 | 0.7481 | 0.7481 |
| 5 | 0.8148 | 0.8148 |
| 8 | 0.8642 | 0.8642 |

*Hybrid search esperado: +5-10% en P@3 (pendiente correr)*
