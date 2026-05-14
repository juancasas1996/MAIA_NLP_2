"""
Standalone chunker extraído de textsplitter.py (sin dependencias de app/).
Usa SentenceTextSplitter de Microsoft (adaptado) para dividir documentos Markdown
en chunks semánticos preservando límites de oración y token budget de bge-small-en-v1.5.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, List

import tiktoken

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes (antes en app/prepdocslib/page.py)
# ---------------------------------------------------------------------------

@dataclass
class Page:
    """Representa una "página" de texto (para docs Markdown usamos page_num=0)."""
    page_num: int
    offset: int   # posición en caracteres dentro del texto completo del documento
    text: str


@dataclass
class SplitPage:
    """Un chunk resultante del splitter."""
    page_num: int
    text: str
    pages_included: List[int] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Constantes (antes leídas de app.utils.settings)
# ---------------------------------------------------------------------------

SECTION_LENGTH   = 800    # chars por chunk — docs técnicos cortos
OVERLAP_PERCENT  = 0.20   # 20 % de solapamiento entre chunks consecutivos
MAX_TOKENS       = 400    # límite duro de tokens (bge-small-en-v1.5 acepta máx 512)

SENTENCE_ENDINGS = [".", "!", "?", "。", "！", "？", "‼", "⁇", "⁈", "⁉"]
WORD_BREAKS      = [
    ",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n",
    # CJK
    "、", "，", "；", "：", "（", "）", "【", "】", "「", "」",
    "『", "』", "〔", "〕", "〈", "〉", "《", "》",
]

# cl100k_base es el mismo encoding que usa text-embedding-ada-002 / text-embedding-3
_bpe = tiktoken.get_encoding("cl100k_base")


# ---------------------------------------------------------------------------
# Splitter
# ---------------------------------------------------------------------------

class SentenceTextSplitter:
    """
    Divide texto en secciones optimizadas para embeddings respetando límites de
    oración y un presupuesto máximo de tokens por chunk.

    Algoritmo extraído de textsplitter.py (tecbot-normatividad) de Microsoft,
    adaptado para uso standalone sin dependencias de Azure.
    """

    def __init__(
        self,
        section_length: int = SECTION_LENGTH,
        overlap_pct: float = OVERLAP_PERCENT,
        max_tokens: int = MAX_TOKENS,
        sentence_search_limit: int = 100,
    ):
        self.max_section_length   = section_length
        self.section_overlap      = int(section_length * overlap_pct)
        self.max_tokens           = max_tokens
        self.sentence_search_limit = sentence_search_limit
        self.sentence_endings     = SENTENCE_ENDINGS
        self.word_breaks          = WORD_BREAKS

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _count_tokens(self, text: str) -> int:
        return len(_bpe.encode(text))

    def _split_by_max_tokens(
        self,
        page_num: int,
        text: str,
        pages: List[Page],
        pages_included: List[int],
    ) -> Generator[SplitPage, None, None]:
        """Divide recursivamente si el chunk excede el presupuesto de tokens."""
        if self._count_tokens(text) <= self.max_tokens:
            yield SplitPage(page_num=page_num, text=text, pages_included=pages_included)
        else:
            middle  = len(text) // 2
            overlap = int(len(text) * OVERLAP_PERCENT)
            yield from self._split_by_max_tokens(page_num, text[: middle + overlap], pages, pages_included)
            yield from self._split_by_max_tokens(page_num, text[middle - overlap :], pages, pages_included)

    def _find_page(self, offset: int, pages: List[Page]) -> int:
        for i in range(len(pages) - 1):
            if pages[i].offset <= offset < pages[i + 1].offset:
                return pages[i].page_num
        return pages[-1].page_num

    def _pages_included(self, start: int, end: int, pages: List[Page]) -> List[int]:
        return [
            p.page_num + 1
            for p in pages
            if not (end <= p.offset or start >= p.offset + len(p.text))
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def split_pages(self, pages: List[Page]) -> Generator[SplitPage, None, None]:
        """Divide el contenido completo de las páginas en chunks semánticos."""
        all_text = "".join(p.text for p in pages)
        if not all_text.strip():
            return

        length = len(all_text)

        # Documento suficientemente corto → un solo chunk (con verificación de tokens)
        if length <= self.max_section_length:
            yield from self._split_by_max_tokens(
                page_num=self._find_page(0, pages) + 1,
                text=all_text,
                pages=pages,
                pages_included=self._pages_included(0, length, pages),
            )
            return

        start = 0
        while start + self.section_overlap < length:
            end = min(start + self.max_section_length, length)
            last_word = -1

            if end < length:
                # Avanzar hasta el final de oración (dentro del límite de búsqueda)
                while (
                    end < length
                    and (end - start - self.max_section_length) < self.sentence_search_limit
                    and all_text[end] not in self.sentence_endings
                ):
                    if all_text[end] in self.word_breaks:
                        last_word = end
                    end += 1
                if end < length and all_text[end] not in self.sentence_endings and last_word > 0:
                    end = last_word

            if end < length:
                end += 1

            # Ajustar inicio al comienzo de oración
            last_word = -1
            while (
                start > 0
                and start > end - self.max_section_length - 2 * self.sentence_search_limit
                and all_text[start] not in self.sentence_endings
            ):
                if all_text[start] in self.word_breaks:
                    last_word = start
                start -= 1
            if all_text[start] not in self.sentence_endings and last_word > 0:
                start = last_word
            if start > 0:
                start += 1

            section_text    = all_text[start:end]
            pages_included  = self._pages_included(start, end, pages)
            page_num        = self._find_page(start, pages) + 1

            yield from self._split_by_max_tokens(page_num, section_text, pages, pages_included)

            # Si termina con una figura XML abierta, incluirla en el siguiente chunk
            last_fig_start = section_text.rfind("<figure")
            if (
                last_fig_start > 2 * self.sentence_search_limit
                and last_fig_start > section_text.rfind("</figure")
            ):
                start = min(end - self.section_overlap, start + last_fig_start)
            else:
                start = end - self.section_overlap

        # Último tramo residual
        if start + self.section_overlap < length:
            pages_included = self._pages_included(start, length, pages)
            page_num       = self._find_page(start, pages)
            yield from self._split_by_max_tokens(page_num, all_text[start:length], pages, pages_included)


# ---------------------------------------------------------------------------
# Adaptador para archivos Markdown
# ---------------------------------------------------------------------------

def load_markdown_as_pages(md_path: str) -> List[Page]:
    """Lee un archivo .md y lo convierte en una lista con un único Page."""
    text = Path(md_path).read_text(encoding="utf-8")
    return [Page(page_num=0, offset=0, text=text)]


# ---------------------------------------------------------------------------
# Smoke test rápido
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path:
        pages  = load_markdown_as_pages(path)
        chunks = list(SentenceTextSplitter().split_pages(pages))
        print(f"{len(chunks)} chunks generados desde '{path}'")
        for i, c in enumerate(chunks[:3]):
            print(f"\n--- Chunk {i} ({len(c.text)} chars) ---\n{c.text[:200]}...")
    else:
        # Test mínimo
        splitter = SentenceTextSplitter(section_length=200, overlap_pct=0.1, max_tokens=100)
        sample   = [Page(page_num=0, offset=0, text="Hello world. " * 50)]
        chunks   = list(splitter.split_pages(sample))
        assert chunks, "No chunks generados"
        print(f"OK — {len(chunks)} chunks generados en smoke test.")
