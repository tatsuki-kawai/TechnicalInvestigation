import spacy
import MeCab

from janome.tokenizer import Tokenizer
from janome.analyzer import Analyzer
from janome.charfilter import *
from janome.tokenfilter import *

class Kakariuke:
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

class WordDividerJanome:
    def __init__(self):
        self.wakati_analyzer = Analyzer(token_filters=[CompoundNounFilter(), ExtractAttributeFilter('base_form')])
        self.wakati = Analyzer(token_filters=[CompoundNounFilter()])
        self.t = Tokenizer()

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
        wakati = list(self.wakati.analyze(text))
        for word in wakati:
            words.append(word)

        output = ""
        for word in words:
            output += word
            output += " "
        return output

    def wakati_text_delete(self, text, stop_word_list=[]):
        if not text:
            return []
        malist = self.wakati.analyze(text)
        words = []
        for w in malist:
            word = w.base_form
            ps = w.part_of_speech.split(',')
            #print(word, w.part_of_speech)
            if ('名詞' in ps and '非自立' not in ps) or '形容詞' in ps or ('動詞' in ps and '接尾' not in ps):
                if word not in stop_word_list:
                    words.append(word)
        output = ""
        for word in words:
            output += word
            output += " "
        return output

    def wakati_text_hukugou_delete(self, text, stop_word_list=[]):
        if not text:
            return []
        malist = self.wakati.analyze(text)
        words = []
        for w in malist:
            word = w.base_form
            ps = w.part_of_speech.split(',')
            #print(word, w.part_of_speech)
            if ('名詞' in ps and '非自立' not in ps) or '形容詞' in ps or ('動詞' in ps and '接尾' not in ps):
                if word not in stop_word_list:
                    words.append(word)
        output = ""
        for word in words:
            output += word
            output += " "
        return output

class WordDividerMecab:
    def __init__(self):
        # Mecab.Taggerの引数がコマンドラインの引数と同じ
        self.tagger = MeCab.Tagger()

    def wakati_text_delete(self, text, stop_word_list=[]):
        if not text:
            return []
        maList = self.tagger.parse(text).split('\n')
        words = []
        for element in maList:
            list = element.split("\t")
            if len(list) == 1:
                continue
            word = list[0]
            ps = list[1].split(",")
            word_base_form = ps[6]
            if ('名詞' in ps or '形容詞' in ps or '動詞' in ps) and ("非自立" not in ps and "接尾" not in ps and "代名詞" not in ps):
                if word_base_form not in stop_word_list:
                    words.append(word_base_form)
        output = ""
        for word in words:
            output += word
            output += " "
        return output