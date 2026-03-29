import spacy
from typing import List, Dict

class NLPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            try:
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = spacy.blank("en")

    def process(self, text: str) -> Dict:
        doc = self.nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        keywords = [chunk.text for chunk in doc.noun_chunks]
        cleaned = " ".join(
            [t.lemma_.lower() for t in doc if not t.is_stop and not t.is_punct and t.is_alpha]
        )
        return {
            "entities": entities,
            "keywords": keywords,
            "cleaned_text": cleaned,
        }

    def extract_entities(self, text: str) -> List[Dict]:
        doc = self.nlp(text)
        return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]