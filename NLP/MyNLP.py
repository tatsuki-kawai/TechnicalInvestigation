from janome.tokenizer import Tokenizer

class WordDivider:
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
