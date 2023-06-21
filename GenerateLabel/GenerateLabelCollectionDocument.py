# WordSurfacePhraseクラスはGenerateLabelCollectionDocumentクラスを改良したものである。

import sys
sys.path.append('../NLP')

from MyNLP import WordDividerMecab, WordDividerJanome, Kakariuke
from itertools import combinations
import itertools
import math


class WordSurfacePhrase:
    def __init__(self, collection=[], stop_word_list=["、", "。"], appear_tagging_list=[], stop_tagging_list=[]): # 入力は未加工のデータ
        # 分かち書きを行う
        wakati_collection = []
        wd = WordDividerJanome()
        for item in collection:
            wakati_text = wd.wakati_text_surface(text=item, stop_word_list=stop_word_list,
                                                 appear_tagging_list=appear_tagging_list,
                                                 stop_tagging_list=stop_tagging_list)
            wakati_collection.append(wakati_text)

        # スペースの除去
        word_collection = []
        for item in wakati_collection:
            word_collection.append(item.split(" "))
        self.collection = word_collection

    def ngram_extract_phrase_mi(self, ngram, threshold=False, threshold_score=0):
        phrase_word_lists = []
        for text in self.collection:
            phrase_word_list = []
            print(text)
            for index in range(len(text) - ngram):
                phrase = text[index]
                for n in range(1, ngram):
                    phrase += text[index + n]
                words = text[index:index + ngram]
                phrase_word_list.append([phrase, words])
            phrase_word_lists.append(phrase_word_list)

        # ここからがスコアの計算
        phrase_word_score_list = []
        flattened_phrase_word_list = list(itertools.chain(*phrase_word_lists))
        word_list = list(itertools.chain(*self.collection))
        phrase_list = [phrase_word[0] for phrase_word in flattened_phrase_word_list]
        for phrase, words in flattened_phrase_word_list:
            # 分子の計算
            phrase_frequency = phrase_list.count(phrase) / len(phrase_list)

            # 分母の計算
            word_frequency = 1
            for n in range(0, ngram):
                word = words[n]
                word_frequency = word_frequency * (word_list.count(word) / len(word_list))

            # 対数の計算
            mi_score = math.log(phrase_frequency / word_frequency)

            # 各種数値の表示
            # print(f"phrase_frequency = {phrase_frequency}") # 分子
            # print(f"word_frequency = {word_frequency}") # 分母
            # print(f"mi_score = {mi_score}")
            if threshold is True:
                if mi_score >= threshold_score:
                    phrase_word_score_list.append([phrase, words, mi_score])
            else:
                phrase_word_score_list.append([phrase, words, mi_score])
        return phrase_word_score_list

    def caluculate_watf(self, phrase_word_score_list):
        phrase_word_watf_list = []
        word_list = list(itertools.chain(*self.collection))
        for phrase_word_score in phrase_word_score_list:
            sum = 0
            word_count = len(phrase_word_score[1])
            for m in range(word_count):
                word = phrase_word_score[1][m]
                sum += word_list.count(word)
            watf = math.sqrt(word_count) * (sum / word_count)
            phrase_word_watf_list.append([phrase_word_score[0], phrase_word_score[1], phrase_word_score[2], watf])

        # ランキング形式で並べる
        phrase_word_watf_list.sort(key=lambda x: x[3], reverse=True)

        return phrase_word_watf_list

    def ngram_extract_phrase_rank_watf(self, ngram=2, threshold=False, threshold_score=0):
        phrase_word_score_list = self.ngram_extract_phrase_mi(ngram=ngram, threshold=threshold, threshold_score=threshold_score)
        return self.caluculate_watf(phrase_word_score_list)

    def ngram_range_extract_phrase_rank_watf(self, start_n, end_n, threshold=False, threshold_score=0):
        # 閾値（threshold）が現状ひとつしか設定できていないため、あまり適切ではない。
        phrase_word_score_lists = []
        for n in range(start_n, end_n+1):
            phrase_word_score_list = self.ngram_extract_phrase_mi(ngram=n, threshold=threshold, threshold_score=threshold_score)
            phrase_word_score_lists.append(phrase_word_score_list)
        flattened_phrase_word_score_list = list(itertools.chain(*phrase_word_score_lists))
        return self.caluculate_watf(flattened_phrase_word_score_list)

class GenerateLabelCollectionDocument:
    def __init__(self, collection=[]): # 入力は未加工のデータ
        self.collection = collection

    def wakati_mecab_collection(self, stop_word_list=[], appear_tagging_list=[], stop_tagging_list=[]):
        new_collection = []
        wd = WordDividerMecab()
        for item in self.collection:
            wakati_text = wd.wakati_text(text=item, stop_word_list=stop_word_list, appear_tagging_list=appear_tagging_list,
                                         stop_tagging_list=stop_tagging_list)
            new_collection.append(wakati_text)
        self.collection = new_collection

    def wakati_janome_surface_collection(self, stop_word_list=[], appear_tagging_list=[], stop_tagging_list=[]):
        new_collection = []
        wd = WordDividerJanome()
        for item in self.collection:
            wakati_text = wd.wakati_text_surface(text=item, stop_word_list=stop_word_list, appear_tagging_list=appear_tagging_list,
                                         stop_tagging_list=stop_tagging_list)
            new_collection.append(wakati_text)
        self.collection = new_collection

    def wakati_janome_base_form_collection(self, stop_word_list=[], appear_tagging_list=[], stop_tagging_list=[]):
        new_collection = []
        wd = WordDividerJanome()
        for item in self.collection:
            wakati_text = wd.wakati_text_base_form(text=item, stop_word_list=stop_word_list, appear_tagging_list=appear_tagging_list,
                                         stop_tagging_list=stop_tagging_list)
            new_collection.append(wakati_text)
        self.collection = new_collection

    def split_space_collection(self):
        new_collection = []
        for item in self.collection:
            new_collection.append(item.split(" "))
        self.collection = new_collection

    def frequent_word(self):
        self.wakati_janome_surface_collection()
        splited_text_by_words = []
        for i in self.collection:
            splited_text_by_words.append(i.split())

        word_count = {}
        for text in splited_text_by_words:
            for word in text:
                if word in word_count:
                    word_count[word] += 1
                else:
                    word_count[word] = 1

        sorted_word_count = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

        for word, count in sorted_word_count:
            print(word, count)

    def ngram_extract_phrase_mi(self, ngram, threshold=0):
        self.wakati_janome_surface_collection(stop_word_list=["、", "。"])
        self.split_space_collection()

        phrase_word_lists = []
        for text in self.collection:
            phrase_word_list = []
            print(text)
            for index in range(len(text)-ngram):
                phrase = text[index]
                for n in range(1, ngram):
                    phrase += text[index+n]
                words = text[index:index + ngram]
                phrase_word_list.append([phrase, words])
            phrase_word_lists.append(phrase_word_list)

        # ここからがスコアの計算
        phrase_word_score_list = []
        flattened_phrase_word_list = list(itertools.chain(*phrase_word_lists))
        word_list = list(itertools.chain(*self.collection))
        phrase_list = [phrase_word[0] for phrase_word in flattened_phrase_word_list]
        for phrase, words in flattened_phrase_word_list:
            # 分子の計算
            phrase_frequency = phrase_list.count(phrase) / len(phrase_list)

            # 分母の計算
            word_frequency = 1
            for n in range(0, ngram):
                word = words[n]
                word_frequency = word_frequency * (word_list.count(word) / len(word_list))

            # 対数の計算
            mi_score = math.log(phrase_frequency / word_frequency)

            # 各種数値の表示
            # print(f"phrase_frequency = {phrase_frequency}") # 分子
            # print(f"word_frequency = {word_frequency}") # 分母
            # print(f"mi_score = {mi_score}")

            if mi_score >= threshold:
                phrase_word_score_list.append([phrase, words, mi_score])
        return phrase_word_score_list

    def ngram_range_extract_phrase(self, start_n, end_n):
        #　製作途中(MIを求めていないので注意）
        self.wakati_janome_surface_collection(stop_word_list=["、", "。"])
        self.split_space_collection()
        phrase_word_lists = []
        for text in self.collection:
            # print(text)
            phrase_word_list = []

            for i_gram in range(start_n, end_n + 1):
                for index in range(len(text) - i_gram):
                    phrase = text[index]
                    for n in range(1, i_gram):
                        phrase += text[index + n]
                    words = text[index:index + i_gram]
                    phrase_word_list.append([phrase, words])
            phrase_word_lists.append(phrase_word_list)
        return phrase_word_lists

    def ngram_extract_phrase_rank_watf(self, ngram=2, threshold=0):
        # 制作途中
        phrase_word_score_list = self.ngram_extract_phrase_mi(ngram=ngram, threshold=threshold)

        phrase_word_watf_list = []
        # ここからがWATFの計算
        word_list = list(itertools.chain(*self.collection))
        for phrase_word_score in phrase_word_score_list:
            sum = 0
            word_count = len(phrase_word_score[1])
            for m in range(word_count):
                word = phrase_word_score[1][m]
                sum += word_list.count(word)
            watf = math.sqrt(word_count) * (sum / word_count)
            phrase_word_watf_list.append([phrase_word_score[0], phrase_word_score[1], phrase_word_score[2], watf])

        # ランキング形式で並べる
        phrase_word_watf_list.sort(key=lambda x: x[3], reverse=True)

        return phrase_word_watf_list

















