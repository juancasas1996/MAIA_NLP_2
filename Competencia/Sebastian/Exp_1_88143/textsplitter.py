# File: app/prepdocslib/textsplitter.py
import logging
from abc import ABC
from typing import Generator, List
from app.utils.settings import settings
import tiktoken
from .page import Page, SplitPage

logger = logging.getLogger("scripts")


class TextSplitter(ABC):
    """
    Divide una lista de páginas (`Page`) en fragmentos (`SplitPage`)
    """

    def split_pages(self, pages: List[Page]) -> Generator[SplitPage, None, None]:
        if False:
            yield  # pragma: no cover - this is necessary for mypy to type check


# Modelo de referencia para la codificación BPE
ENCODING_MODEL = "text-embedding-ada-002"

# Caracteres que indican ruptura de palabra
STANDARD_WORD_BREAKS = [",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n"]

# See W3C document https://www.w3.org/TR/jlreq/#cl-01
# Caracteres equivalentes para lenguajes CJK (chino, japonés, coreano)
CJK_WORD_BREAKS = [
"、","，","；","：","（","）","【","】","「","」","『","』",
"〔","〕","〈","〉","《","》","〖","〗","〘","〙","〚","〛",
"〝","〞","〟","〰","–","—","‘","’","‚","‛","“","”","„",
"‟","‹","›"
]

# Finales de oración en inglés
STANDARD_SENTENCE_ENDINGS = [".", "!", "?"]

# Finales de oración en lenguajes CJK
CJK_SENTENCE_ENDINGS = ["。", "！", "？", "‼", "⁇", "⁈", "⁉"]

# Codificador BPE del modelo seleccionado (ada-002 y text-embedding-3 comparten el mismo)
bpe = tiktoken.encoding_for_model(ENCODING_MODEL)


DEFAULT_OVERLAP_PERCENT = settings.overlap_percent
"""
Porcentaje de solapamiento entre secciones consecutivas. 
Ej: Si DEFAULT_OVERLAP_PERCENT = 30 y DEFAULT_SECTION_LENGTH = 1000, entonces:
	•	Chunk 1: caracteres del 0 al 1000
	•	Chunk 2: comienza en el 700 (porque 1000 - 300) y va hasta el 1700
	•	Chunk 3: comienza en el 1400 y así sucesivamente
"""


DEFAULT_SECTION_LENGTH = settings.section_length
"""
Tamaño base (en caracteres) de cada sección antes de dividir por tokens. 
"""



MAX_TOKENS_PER_SECTION = settings.max_tokens_per_section
"""
Límite duro de tokens permitidos por sección. Si una sección supera este límite, se divide recursivamente.
Esto previene errores en el modelo de embeddings por inputs demasiado largos.
"""


# ----------------------
# Splitter principal
# ----------------------

class SentenceTextSplitter(TextSplitter):
    """
    Divide texto en secciones optimizadas para embeddings. 
    Usa puntuación, ruptura de palabras y longitud en tokens para cortar inteligentemente el texto.

    Esta clase está diseñada para preservar la coherencia semántica y no cortar oraciones arbitrariamente.
    """

    def __init__(self, max_tokens_per_section: int = MAX_TOKENS_PER_SECTION):
        self.sentence_endings = STANDARD_SENTENCE_ENDINGS + CJK_SENTENCE_ENDINGS
        self.word_breaks = STANDARD_WORD_BREAKS + CJK_WORD_BREAKS
        self.max_section_length = DEFAULT_SECTION_LENGTH
        self.sentence_search_limit = 100
        self.max_tokens_per_section = max_tokens_per_section
        self.section_overlap = int(self.max_section_length * DEFAULT_OVERLAP_PERCENT / 100)


    def split_page_by_max_tokens(self,page_num: int,text: str,pages: List[Page],start_offset: int = 0,pages_included: List[int] = None) -> Generator[SplitPage, None, None]:
        """
        Divide recursivamente un bloque de texto si excede el número máximo de tokens permitidos.
        """

        tokens = bpe.encode(text)
        if len(tokens) <= self.max_tokens_per_section:
            yield SplitPage(page_num=page_num, text=text, pages_included=pages_included)

        else:
            middle = int(len(text) // 2)
            overlap = int(len(text) * (DEFAULT_OVERLAP_PERCENT / 100))
            first_half = text[: middle + overlap]
            second_half = text[middle - overlap :]

            yield from self.split_page_by_max_tokens(page_num, first_half, pages, start_offset, pages_included)
            yield from self.split_page_by_max_tokens(page_num, second_half, pages, start_offset + middle - overlap, pages_included)





    def split_pages(self, pages: List[Page]) -> Generator[SplitPage, None, None]:
        """
        Divide el contenido completo de las páginas en secciones menores (chunks),
        respetando oraciones y límites de tokens.
        """

        def find_page(offset):
            num_pages = len(pages)
            for i in range(num_pages - 1):
                if offset >= pages[i].offset and offset < pages[i + 1].offset:
                    return pages[i].page_num
                
            return pages[num_pages - 1].page_num

        all_text = "".join(page.text for page in pages)
        if len(all_text.strip()) == 0:
            return

        length = len(all_text)
        if length <= self.max_section_length:

            pages_included = self.get_pages_included(0, len(all_text), pages)
            yield from self.split_page_by_max_tokens(
                page_num=find_page(0) + 1,
                text=all_text,
                pages=pages,
                start_offset=0,
                pages_included=pages_included
            )

            return

        start = 0
        end = length
        while start + self.section_overlap < length:
            last_word = -1
            end = start + self.max_section_length

            if end > length:
                end = length
            else:
                # Buscar el final de la oración o al menos una palabra entera
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

            # Buscar el inicio de la oración o al menos una palabra entera
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

            section_text = all_text[start:end]


            pages_included = self.get_pages_included(start, end, pages)
            yield from self.split_page_by_max_tokens(
                page_num=find_page(start) + 1,
                text=section_text,
                pages=pages,
                start_offset=start,
                pages_included=pages_included
            )



            # Si la sección termina con una figura sin cerrar, incluirla en el próximo chunk
            last_figure_start = section_text.rfind("<figure")
            if last_figure_start > 2 * self.sentence_search_limit and last_figure_start > section_text.rfind(
                "</figure"
            ):
                # If the section ends with an unclosed figure, we need to start the next section with the figure.
                start = min(end - self.section_overlap, start + last_figure_start)
                logger.info(f"Section ends with unclosed figure, starting next section with the figure at page {find_page(start)} offset {start} figure start {last_figure_start}")

            else:

                start = end - self.section_overlap


        if start + self.section_overlap < end:
            pages_included = self.get_pages_included(start, end, pages)
            yield from self.split_page_by_max_tokens(
                page_num=find_page(start),
                text=all_text[start:end],
                pages=pages,
                start_offset=start,
                pages_included=pages_included
            )




    
    def get_pages_included(self, start_offset: int, end_offset: int, pages: List[Page]) -> List[int]:
        """
        Devuelve una lista con los números de página que están cubiertos 
        por el fragmento de texto entre `start_offset` y `end_offset`.
        """

        return [
            page.page_num + 1
            for page in pages
            if not (end_offset <= page.offset or start_offset >= page.offset + len(page.text))
        ]

