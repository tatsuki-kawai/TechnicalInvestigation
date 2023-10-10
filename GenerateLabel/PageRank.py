import sys
sys.path.append('../NLP')

from MyNLP import WordDividerMecab, WordDividerJanome, Kakariuke
from sklearn.feature_extraction.text import TfidfVectorizer
from itertools import combinations
import itertools
import math
import numpy as np
import spacy

class WordGraph:
    def __init__(self, collection=[], stop_word_list=[], appear_tagging_list=[], stop_tagging_list=[], w=2):
        # 入力は未加工のデータ(例：「私はご飯を食べる。」)
        # 分かち書きを行う
        wakati_collection = []
        wd = WordDividerMecab()
        for item in collection:
            wakati_text = wd.wakati_text(text=item, stop_word_list=stop_word_list,
                                         appear_tagging_list=appear_tagging_list,
                                         stop_tagging_list=stop_tagging_list)
            wakati_collection.append(wakati_text)

        # データセット内での語彙リストの作成
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(wakati_collection)
        self.voc = sorted(vectorizer.vocabulary_)

        # スペースの除去
        word_collection = []
        for item in wakati_collection:
            item = item.split(" ")
            item.remove("")
            word_collection.append(item)

        self.collection = word_collection

        # 共起関係を格納するリストの作成
        comment_list = self.collection
        vocabulary = self.voc
        window_size = w

        self.co_occurrence_list = [np.zeros(len(vocabulary)) for i in range(len(vocabulary))]

        for comment in comment_list:
            # for index in range(len(comment) - window_size + 1):
            for index in range(len(comment)):
                window_words = comment[index:index+window_size]
                index_word = window_words[0]
                co_occurrence_words = window_words[1:]

                # print(f"window_words:{window_words}")
                # print(f"index_word:{index_word}")
                # print(f"co_occurrence_word:{co_occurrence_words}")

                if index_word in vocabulary:
                    index_word_id = vocabulary.index(index_word)
                    for co_occurrence_word in co_occurrence_words:
                        if co_occurrence_word in vocabulary:
                            co_occurrence_word_id = vocabulary.index(co_occurrence_word)
                            self.co_occurrence_list[index_word_id][co_occurrence_word_id] += 1

class TopicalPageRank:
    def __init__(self, collection=[], stop_word_list=[], appear_tagging_list=[], stop_tagging_list=[], w=2):
        self.collection = collection
        self.word_graph = WordGraph(collection=collection, stop_word_list=stop_word_list,
                                    appear_tagging_list=appear_tagging_list, stop_tagging_list=stop_tagging_list, w=w)
        self.word_score_list = []

    def calculate(self, damping_factor=0.4, word_weighted_list=[]):
        # word_weightedは[['ご飯', 33.0], ['明日', 6.0]]のような形で渡してください。
        vocabulary = self.word_graph.voc
        co_occurrence_list = self.word_graph.co_occurrence_list
        word_score_list = [1/len(vocabulary) for voc in range(len(vocabulary))]

        # print(vocabulary)
        # print(co_occurrence_list)

        rink_wights_sum = [sum(co_occurrence) for co_occurrence in co_occurrence_list]  # O(wi)のリスト, リンクの重みの総和のリスト

        new_word_weighted_list = np.zeros(len(vocabulary))
        node_count = len(vocabulary)  # 頂点の数

        sum_word_weighted = 0
        if len(word_weighted_list) != 0:
            for word_weighted in word_weighted_list:
                word = word_weighted[0]
                weighted = word_weighted[1]

                if word in vocabulary:
                    word_index = vocabulary.index(word)
                    new_word_weighted_list[word_index] = weighted
                    sum_word_weighted += weighted

        # print(f"sum_word_weighted:{sum_word_weighted}")
        # print(f"new_word_weighted_list:{new_word_weighted_list}")

        iterations_count = 0
        while iterations_count < 100:
            # 各単語のスコアを再計算する
            for word_score_i_index, word_score_i in enumerate(word_score_list):
                # 接続している単語スコアの総和を求める
                word_score_j_sum = 0
                word_probability = 0
                if len(word_weighted_list) != 0:
                    if sum_word_weighted != 0:
                        word_probability = new_word_weighted_list[word_score_i_index] / sum_word_weighted
                # print(f"word_score_word:{vocabulary[word_score_i_index]}")
                for co_occurrence_index, co_occurrence in enumerate(co_occurrence_list):
                    if word_score_i_index != co_occurrence_index and co_occurrence[word_score_i_index] != 0:
                        rink_wights = co_occurrence[word_score_i_index]
                        word_score_j = word_score_list[co_occurrence_index]

                        word_score_j_sum += (rink_wights / rink_wights_sum[co_occurrence_index]) * word_score_j

                        # print(f"co_occurrence_word:{vocabulary[co_occurrence_index]}, rink_wights:{rink_wights}")
                if len(word_weighted_list) != 0:
                    # print(f"word:{vocabulary[word_score_i_index]}, word_probability:{word_probability}")
                    word_score_list[word_score_i_index] = (damping_factor * word_score_j_sum) + (1 - damping_factor) * word_probability
                else:
                    word_score_list[word_score_i_index] = (damping_factor * word_score_j_sum) + (1 - damping_factor) * (1 / node_count)
            # print(f"{iterations_count}:{word_score_list}")
            iterations_count += 1
        self.word_score_list = word_score_list
        return word_score_list

    def extract_phrase(self, damping_factor=0.4, word_weighted_list=[]):
        # フレーズ候補の抽出
        nlp: spacy.Language = spacy.load('ja_ginza')

        noun_list = []
        chunk_list = []
        wd = WordDividerMecab()
        collection = self.collection
        for item in collection:
            item = nlp(item.replace("\n", ""))
            for chunks in item.noun_chunks:
                if chunks.text not in chunk_list:
                    wakati_text = wd.wakati_text(text=chunks.text)
                    wakati_words = wakati_text.split(" ")
                    wakati_words.remove("")
                    noun_list.append([chunks.text, wakati_words])
                    chunk_list.append(chunks.text)

        # フレーズのランク付け
        word_score_list = self.calculate(damping_factor=damping_factor, word_weighted_list=word_weighted_list)
        vocabulary = self.word_graph.voc

        noun_score_list = []
        for noun in noun_list:
            total_noun_score = 0
            noun_chunks = noun[0]
            noun_word_list = noun[1]

            # ラベル(名詞句)のスコアを計算する
            for noun_word in noun_word_list:
                if noun_word in vocabulary:
                    noun_word_index = vocabulary.index(noun_word)
                    noun_score = word_score_list[noun_word_index]
                    total_noun_score += noun_score

            # スコアの計算(修正前)　フレーズの長さを考慮する
            noun_score_list.append([noun_chunks, noun_word_list, total_noun_score / len(noun_word_list)])

            """
            def remove_phrase(noun_word_list): # 複数の単語で生成されている要素か判定
                return len(noun_word_list) > 1

            noun_score_list = [noun_score for noun_score in noun_score_list if remove_phrase(noun_score[1])]
            

            # スコアの計算(修正後)　フレーズの長さを考慮しない
            # noun_score_list.append([noun_chunks, noun_word_list, total_noun_score])
            """

            # スコアを基にソートする
            noun_score_list.sort(key=lambda x: x[2], reverse=True)
        return noun_score_list


def main():
    list = ['紛失時のリスクをマイナカードに集約してしまうと、再発行されるまで病院にいけない、車にも乗れない、となりますね。',
            '保健証1枚、免許証１枚だけでなく紛失時は財産丸ごと落とすことになりますね。',
            '紛失時に１回ですべて事足りるという解釈もありますが、そうなるとマイナ紛失して紛失にかかわる手続きすると口座も保険証も免許証もクレカも１度に全部、停止になるのかな・・・。',
            'そうすれば、不携帯での取締対象にならないし、利用する側も紛失リスクは下げられますしね。',
            'あれだけ変化球を多投していると肘にも負担がかかります、やはり定期的に休養が必要ということですね、来年の開幕戦復帰を楽しみにしています。'
            "来年度は打者オンリーで、再来年から二刀流復帰という計画とあります"]
    # list = ['今日は田中がご飯を食べるが田中がご飯を作ったわけではない。']
    wg = WordGraph(collection=list, appear_tagging_list=["名詞", "形容詞"], w=10)
    tpr = TopicalPageRank(collection=list, appear_tagging_list=["名詞", "形容詞"], w=10)
    print(tpr.word_graph.voc)
    print(tpr.calculate(word_weighted_list=[['紛失', 31.0], ['発行', 30.0], ['リスク', 14.0], ['無くす', 14.0], ['病院', 13.0]]))
    print(tpr.extract_phrase(word_weighted_list=[['紛失', 31.0], ['発行', 30.0], ['リスク', 14.0], ['無くす', 14.0], ['病院', 13.0]]))

    # print(f"word_score_list:{tpr.calculate()}")
    # print(wg.collection)
    # print(wg.voc)
    # print(wg.co_occurrence_list)

if __name__ == '__main__':
        main()



