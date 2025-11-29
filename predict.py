from typing import List
import re
import pdfplumber
from cog import BasePredictor, Input, Path


class Predictor(BasePredictor):
    def setup(self):
        # Für spätere OCR-Erweiterungen wäre hier Platz
        pass

    def predict(
        self,
        pdf_file: Path = Input(
            description="PDF-Datei hochladen (Nicht-OCR-Version – für 'echten' Text)."
        ),
        max_pages: int = Input(
            description="Wie viele Seiten maximal extrahiert werden sollen.",
            default=200,
            ge=1,
            le=800,
        ),
        remove_headers_footers: bool = Input(
            description="Header/Fußzeilen heuristisch entfernen?",
            default=True,
        ),
    ) -> str:
        """
        PDF → CLEAN TEXT Extractor
        ----------------------------------
        • extrahiert Text aus PDF-Seiten
        • entfernt optional Kopf- & Fußzeilen
        • normalisiert Whitespace
        • gibt KI-freundlichen, komprimierten Text zurück
        """

        texts: List[str] = []

        with pdfplumber.open(str(pdf_file)) as pdf:
            for i, page in enumerate(pdf.pages):
                if i >= max_pages:
                    break

                raw = page.extract_text() or ""
                if not raw.strip():
                    continue

                # Zeilen sauber auftrennen
                lines = [l.strip() for l in raw.splitlines() if l.strip()]

                # Kopf- & Fußzeilen entfernen (grobe Heuristik)
                if remove_headers_footers and len(lines) > 6:
                    body_lines = lines[1:-1]
                else:
                    body_lines = lines

                text_clean = "\n".join(body_lines).strip()
                if text_clean:
                    texts.append(text_clean)

        # Alles zusammenfügen
        full = "\n\n".join(texts)

        # Whitespace bereinigen
        full = re.sub(r"[ \t]+", " ", full)
        full = re.sub(r"\n{3,}", "\n\n", full)

        return full.strip()
