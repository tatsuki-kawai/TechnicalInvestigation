import pandas as pd
import numpy as np
from janome.tokenizer import Tokenizer

class Inui_Dic:
    def __init__(self):
        dic = pd.read_csv(r"http://www.cl.ecei.tohoku.ac.jp/resources/sent_lex/wago.121808.pn",
                          names=["judge_type_word"])
        dic = dic["judge_type_word"].str.split('\t', expand=True)
        dic[0] = dic[0].str.replace(r'\（.*\）', '', regex=True)
        dic[0] = dic[0].str.replace('ネガ', '-1')
        dic[0] = dic[0].str.replace('ポジ', '1')
        neg_pos = dic[0].tolist()
        keys = dic[1].tolist()
        self.dic = dict(zip(keys, neg_pos))

class Takamura_Dic:
    def __init__(self):
        pd.set_option('display.unicode.east_asian_width', True)
        dic = pd.read_csv(r'http://www.lr.pi.titech.ac.jp/~takamura/pubs/pn_ja.dic',
                          encoding='shift-jis', names=["word_type_score"])
        dic = dic["word_type_score"].str.split(':', expand=True)
        keys = dic[0].tolist()
        values = map(float, dic[3].tolist())
        values = map(lambda value: value if value >= 0 else value * 0.5, values)
        dic = dict(zip(keys, values))
        self.dic = dic


class Analyst:
    def __init__(self, dic_type=Takamura_Dic):
        dic_type = dic_type()
        self.dic = dic_type.dic

    def refer_word(self, word):
        if word in self.dic:
            print(f'{word}:{self.dic[word]}')
        else:
            print(f'この辞書には「{word}」は含まれていません')

    def refer_word_sentence(self, sentence):
        word_list = self.split_sentence(sentence)
        for word in word_list:
            self.refer_word(word)

    def split_sentence(self, sentence):
        t = Tokenizer()
        word_list = []
        for token in t.tokenize(sentence):
            word_list.append(token.base_form)
        return word_list

    def word_to_value(self, word_list):
        word_scores = []
        hiteigo = ['ない', 'ず', 'ぬ', 'ん']
        hiteigo_check = []
        for word in word_list:
            # 否定語の有無のチェック
            if word in hiteigo:
                hiteigo_check.append(-1)
            else:
                hiteigo_check.append(1)

            # 形態素の数値化
            if word in self.dic:
                word_score = float(self.dic[f'{word}'])
                if word_score < 0:
                    word_score *= 0.5
                word_scores.append(word_score)
            else:
                word_scores.append(0)
        hiteigo_check.append(1)
        hiteigo_check = hiteigo_check[1:]
        word_score = [x * y for (x, y) in zip(word_scores, hiteigo_check)]
        return word_score

    def inside_calc_pos_neg_score(self, sentence):
        word_list = self.split_sentence(sentence)
        word_score = self.word_to_value(word_list)
        pos_neg_score = sum(word_score)
        print(f'word_list:{word_list}')
        print(f'word_score:{word_score}')
        print(f'score:{pos_neg_score}')
        return pos_neg_score

    def calc_pos_neg_score(self, sentence):
        word_list = self.split_sentence(sentence)
        word_score = self.word_to_value(word_list)
        pos_neg_score = sum(word_score)
        return pos_neg_score

    def calc_pos_neg_ambience_score(self, sentence_list):
        ambience_score = 0
        for sentence in sentence_list:
            sentence_score = self.calc_pos_neg_score(sentence)
            ambience_score += sentence_score
        if len(sentence_list) > 0:
            ambience_score = ambience_score / len(sentence_list)
        else:
            ambience_score = 0
        return ambience_score
