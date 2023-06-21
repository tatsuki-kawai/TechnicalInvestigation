import sys
sys.path.append('../NLP')

from MyNLP import WordDividerMecab, Kakariuke
from itertools import combinations
import itertools
import math

class GenerateLabelCollectionDocument:
    def __init__(self, collection=[]): # 入力は未加工のデータ
        self.collection = collection
    def wakati_collection(self, stop_word_list=[], appear_tagging_list=[], stop_tagging_list=[]):
        new_collection = []
        wd = WordDividerMecab()
        for item in self.collection:
            wakati_text = wd.wakati_text(text=item, stop_word_list=stop_word_list, appear_tagging_list=appear_tagging_list,
                                         stop_tagging_list=stop_tagging_list)
            new_collection.append(wakati_text)
        self.collection = new_collection

    def split_space_collection(self):
        new_collection = []
        for item in self.collection:
            new_collection.append(item.split(" "))
        self.collection = new_collection

    def frequent_word(self):
        self.wakati_collection()
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

    def ngram_extract_phrase_mi(self, ngram):
        self.wakati_collection(stop_word_list=["、", "。"])
        self.split_space_collection()
        phrase_lists = []
        for text in self.collection:
            phrase_list = []
            print(text)
            for index in range(len(text)-ngram):
                phrase = text[index]
                for n in range(1, ngram):
                    phrase += text[index+n]
                words = text[index:index + ngram]
                phrase_list.append([phrase, words])
            phrase_lists.append(phrase_list)

        # ここからがスコアの計算
        mi_score = 0
        total_phrase = sum(len(phrase_list) for phrase_list in phrase_lists)
        new_phrase_list = []
        flattened_phrase_list = list(itertools.chain(*phrase_lists))
        word_list = list(itertools.chain(*self.collection))
        for phrase, words in flattened_phrase_list:
            # 分子の計算
            phrase_frequency = flattened_phrase_list[:][0].count(phrase) / len(flattened_phrase_list[:][0])
            print(flattened_phrase_list)

            # 分母の計算
            word_frequency = 1
            for n in range(0, ngram):
                word = words[n]
                word_frequency = word_frequency * (word_list.count(word) / len(word_list))

            # 対数の計算
            print(phrase_frequency)
            print(word_frequency)
            mi_score = math.log(phrase_frequency / word_frequency)
            print(mi_score)
            new_phrase_list.append([phrase, mi_score])
        return new_phrase_list

    def ngram_range_extract_phrase(self, start_n, end_n):
        #　製作途中
        self.wakati_collection(stop_word_list=["、", "。"])
        self.split_space_collection()
        phrase_lists = []
        for text in self.collection:
            # print(text)
            phrase_list = []
            for i_gram in range(start_n, end_n + 1):
                for index in range(len(text) - i_gram):
                    phrase = text[index]
                    for n in range(1, i_gram):
                        phrase += text[index + n]
                    words = text[index:index + i_gram]
                    phrase_list.append([phrase, words])
            phrase_lists.append(phrase_list)
        return phrase_lists

    def ngram_range_extract_phrase(self, start_n, end_n):
        # 制作途中
        self.wakati_collection(stop_word_list=["、", "。"])
        self.split_space_collection()
        phrase_lists = []
        for text in self.collection:
            # print(text)
            phrase_list = []
            for i_gram in range(start_n, end_n+1):
                for index in range(len(text) - i_gram):
                    phrase = text[index]
                    for n in range(1, i_gram):
                        phrase += text[index + n]
                    words = text[index:index + i_gram]
                    phrase_list.append([phrase, words])
            phrase_lists.append(phrase_list)

            # ここからがWATFの計算
            total_phrase = sum(len(phrase_list) for phrase_list in phrase_lists)

        return phrase_lists
















