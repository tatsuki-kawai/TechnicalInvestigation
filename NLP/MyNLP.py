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

    def trans_newline(self, doc):
        sents = []
        nlp = spacy.load('ja_ginza')
        doc = nlp(doc)
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

    def row_words(self, text):
        if not text:
            return []

        words = []

        for token in self.t.tokenize(text):
            words.append(token)
        return words

    def wakati_text_base_form(self, text, stop_word_list=[], appear_tagging_list=[], stop_tagging_list=[]):
        if not text:
            return []
        malist = self.wakati.analyze(text)
        words = []
        for w in malist:
            word = w.base_form
            ps = w.part_of_speech.split(',')

            if not any(stop_tagging in ps for stop_tagging in stop_tagging_list) and word not in stop_word_list:
                if appear_tagging_list:
                    if any(appear_tagging in ps for appear_tagging in appear_tagging_list):
                        words.append(word)
                else:
                    words.append(word)

        output = ""
        for word in words:
            output += word
            output += " "
        return output

    def wakati_text_surface(self, text, stop_word_list=[], appear_tagging_list=[], stop_tagging_list=[]):
        if not text:
            return []
        malist = self.wakati.analyze(text)
        words = []
        for w in malist:
            word = w.surface
            ps = w.part_of_speech.split(',')

            if not any(stop_tagging in ps for stop_tagging in stop_tagging_list) and word not in stop_word_list:
                if appear_tagging_list:
                    if any(appear_tagging in ps for appear_tagging in appear_tagging_list):
                        words.append(word)
                else:
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

    def wakati_text(self, text, stop_word_list=[], appear_tagging_list=[], stop_tagging_list=[]):
        # 辞書に登録されていない単語は基本形が「＊」になっているので、修正する必要あり。
        # 基本形での分かち書きを行う
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

            if not any(stop_tagging in ps for stop_tagging in stop_tagging_list) and word_base_form not in stop_word_list:
                if appear_tagging_list:
                    if any(appear_tagging in ps for appear_tagging in appear_tagging_list):
                        words.append(word_base_form)
                else:
                    words.append(word_base_form)

        output = ""
        for word in words:
            output += word
            output += " "
        return output

    def wakati_text_henkeinasi(self, text, stop_word_list=[], appear_tagging_list=[], stop_tagging_list=[]):
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

            if not any(stop_tagging in ps for stop_tagging in stop_tagging_list) and word_base_form not in stop_word_list:
                if appear_tagging_list:
                    if any(appear_tagging in ps for appear_tagging in appear_tagging_list):
                        words.append(word_base_form)
                else:
                    words.append(word_base_form)

        output = ""
        for word in words:
            output += word
            output += " "
        return output

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

    def split_text_with_pos_tags(self, text):
        m = MeCab.Tagger("-Ochasen")
        node = m.parse(text)
        split_text = []

        # 各形態素の表層形と品詞を表示する
        for row in node.split("\n"):
            word = row.split("\t")
            if len(word) >= 2:
                pos_tag_list = word[3].split('-')
                input = [word[0], word[3]]
                for pos_tag in pos_tag_list:
                    input.append(pos_tag)
                split_text.append(input)

        return split_text


def main():
    str = 'これはめかぶのてすとです.'
    text = '付かないんだろうだからこんな問題だらけになってる'
    wd = WordDividerMecab()
    wdj = WordDividerJanome()
    output = wd.wakati_text_henkeinasi(str, stop_tagging_list=['格助詞', '副詞可能', '非自立'], appear_tagging_list=['名詞','固有名詞','一般'])
    # output = wd.split_text_with_pos_tags(text)
    output = wdj.wakati_text_surface(text, stop_word_list=["。"])
    print(output)


if __name__ == '__main__':
        main()