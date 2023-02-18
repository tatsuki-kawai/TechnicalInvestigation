import spacy

from janome.tokenizer import Tokenizer

class Divider:
    def __init__(self):
        self.wakati = Tokenizer(wakati=True)
        self.t = Tokenizer()

    def wakati_words(self, text):
        if not text:
            return []

        words = []
        text = list(self.wakati.tokenize(text))
        for word in text:
            words.append(word)

        return words

    def surface_words(self, text):
        if not text:
            return []

        words = []
        for token in self.t.tokenize(text):
            words.append(token.base_form)
        return words

    def wakati_text(self, text):
        if not text:
            return []

        words = []
        wakati = list(self.wakati.tokenize(text))
        for word in wakati:
            words.append(word)

        output = ""
        for word in words:
            output += word
            output += " "
        return output
    
    def text_preprocessing(self, text):
        text = text.replace("\\n", "\n")
        text = text.replace("\n", "")
        return text
    
    def trans_newline(self, text):
        sents = []
        nlp = spacy.load('ja_ginza')
        doc = nlp(text)
        for sent in doc.sents:
            text = sent.text
            sents.append(text)
        return sents
