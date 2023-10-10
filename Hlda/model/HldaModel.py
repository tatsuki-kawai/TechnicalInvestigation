import sys
sys.path.append('../GenerateLabel')
sys.path.append('../NLP')

import pickle
import gzip
import numpy as np
import spacy
import re
from MyNLP import WordDividerMecab, Kakariuke
from hlda.sampler import HierarchicalLDA
from PageRank import TopicalPageRank

class ExpandHldaModel:
    def __init__(self, pickle_path):
        #　改善の余地あり
        if isinstance(pickle_path, str):
            self.hlda = self.load_zipped_pickle(pickle_path)
        else:
            self.hlda = pickle_path

    def save_zipped_pickle(self, filename, protocol=-1):
        with gzip.open(filename, 'wb') as f:
            pickle.dump(self.hlda, f, protocol)

    def load_zipped_pickle(self, filename):
        with gzip.open(filename, 'rb') as f:
            loaded_object = pickle.load(f)
            return loaded_object

    # def print_nodes(self, words, weights):
    #     self.hlda.print_nodes(n_words = words, with_weights = weights)

    def get_document_path(self, doc_index):
        node = self.hlda.document_leaves[doc_index]
        path = []
        while node is not None:
            path.append(node.node_id)
            node = node.parent
        path.reverse()
        return path

    def get_document_path_list(self, corpus):
        document_path_list = []
        for i in range(len(corpus)):
            path = self.get_document_path(i)
            document_path_list.append(path)
        return document_path_list

    def get_topic_document(self, comment_list, corpus, topic_id):
        document_index_list = []
        topic_document_list = []
        path_list = self.get_document_path_list(corpus)
        for i, path in enumerate(path_list):
            if topic_id in path:
                document_index_list.append(i)
        if len(document_index_list) == 0:
            print(f"{topic_id}がみつかりません")
        for i in document_index_list:
            topic_document_list.append(comment_list[i])

        return topic_document_list

    def print_topic_document(self, comment_list, corpus, topic_id):
        topic_document_list = self.get_topic_document(comment_list=comment_list, corpus=corpus, topic_id=topic_id)
        for i, document in enumerate(topic_document_list):
            print(f"No.{i+1}")
            print("「"+document+"」")
            print("")

    def get_node(self, topic_id):
        result = self.explore_node(self.hlda.root_node, topic_id)
        if result is not None:
            return result

    def explore_node(self, node, topic_id):
        if node.node_id == topic_id:
            return node

        for child in node.children:
            result = self.explore_node(child, topic_id)
            if result is not None:
                return result
        return None

    def get_weighted(self, topic_id):
        node = self.get_node(topic_id=topic_id)
        word_weight_pair = []

        if node is None:
            print(f"{topic_id}がみつかりません")
        else:
            pos = np.argsort(node.word_counts)[::-1]
            sorted_vocab = node.vocab[pos]
            sorted_weights = node.word_counts[pos]

            for word, weight in zip(sorted_vocab, sorted_weights):
                word_weight_pair.append([word, weight])

        return word_weight_pair

    def print_topic_phrase_list(self, comment_list, corpus, topic_id, n_phrases):
        topic_document_list = self.get_topic_document(comment_list=comment_list, corpus=corpus,
                                                      topic_id=topic_id)
        tpr = TopicalPageRank(collection=topic_document_list, appear_tagging_list=["名詞", "形容詞"], w=10)
        # topic_word_weighted = expandHlda.get_weighted(topic_id)
        topic_word_weighted = self.get_weighted(topic_id)
        phrase_list = tpr.extract_phrase(damping_factor=0.3, word_weighted_list=topic_word_weighted)
        phrase_list = phrase_list[0:n_phrases]

        for phrase in phrase_list:
            print(phrase)

    def get_topic_phrase_list(self, comment_list, corpus, topic_id, n_phrases):
        topic_document_list = self.get_topic_document(comment_list=comment_list, corpus=corpus,
                                                      topic_id=topic_id)
        tpr = TopicalPageRank(collection=topic_document_list, appear_tagging_list=["名詞", "形容詞"], w=10)
        topic_word_weighted = self.get_weighted(topic_id)
        phrase_list = tpr.extract_phrase(damping_factor=0.3, word_weighted_list=topic_word_weighted)
        phrase_list = phrase_list[0:n_phrases]

        return phrase_list

    def get_topic_phrase(self, comment_list, corpus, topic_id, n_phrases, with_score):
        phrase_list = self.get_topic_phrase_list(comment_list=comment_list, corpus=corpus, topic_id=topic_id, n_phrases=n_phrases)

        output = ""
        for item in phrase_list:
            phrase = item[0]
            score = item[2]
            if np.isnan(score):
                score = 0
            if with_score:
                output += f"{phrase} ({score:.03f}),"
            else:
                output += "%s, " % phrase
        return output

    def print_nodes(self, n_words, weights):
        self.print_node(self.hlda.root_node, 0, n_words, weights)

    def print_node(self, node, indent, n_words, weights):
        out = '    ' * indent
        out += 'topic=%d level=%d (documents=%d): ' % (node.node_id, node.level, node.customers)
        out += node.get_top_words(n_words, weights)
        print(out)
        for child in node.children:
            self.print_node(child, indent + 1, n_words, weights)

    def print_phrases(self, comment_list, corpus, n_phrase, with_score):
        self.print_phrase(self.hlda.root_node, 0, comment_list, corpus, n_phrase, with_score)

    def print_phrase(self, node, indent, comment_list, corpus, n_phrase, with_score):
        out = '    ' * indent

        # 変更前
        # out += 'topic=%d level=%d (documents=%d): ' % (node.node_id, node.level, node.customers)
        #  out += self.get_topic_phrase(comment_list, corpus, node.node_id, n_phrase, with_score)
        # print(out)

        # 変更後
        out += f'topic={node.node_id} '
        out += self.get_topic_phrase(comment_list, corpus, node.node_id, n_phrase, with_score)
        print(out)
        out = ""
        for child in node.children:
            self.print_phrase(child, indent + 1, comment_list, corpus, n_phrase, with_score)

    def get_topic_document_by_sentence(self, comment_list, corpus, topic_id):
        topic_multi_document_by_sentence = self.get_topic_multi_document_by_sentence(comment_list=comment_list,
                                                                                     corpus=corpus)

        get_comment_list = []
        get_topic_sentence_list = []
        for comment_topic_by_sentence in topic_multi_document_by_sentence:
            comment_topic = []

            # コメントが持つトピックを調べる
            for sentence_topic in comment_topic_by_sentence:
                sentence_topic_id = sentence_topic[1]
                if sentence_topic_id not in comment_topic:
                    comment_topic.append(sentence_topic_id)

            # コメントが指定したトピックを持つ場合はリストに追加する
            if topic_id in comment_topic:
                get_comment_list.append(comment_topic_by_sentence)

        for comment in get_comment_list:
            for sentence in comment:
                sentence_str = sentence[0]
                sentence_topic_id = sentence[1]

                if sentence_topic_id == topic_id:
                    get_topic_sentence_list.append(sentence_str)
        return get_topic_sentence_list

    def get_topic_phrase_list_by_sentence(self, comment_list, corpus, topic_id, n_phrases):
        topic_document_list = self.get_topic_document_by_sentence(comment_list=comment_list, corpus=corpus,
                                                                  topic_id=topic_id)
        tpr = TopicalPageRank(collection=topic_document_list, appear_tagging_list=["名詞", "形容詞"], w=10)
        topic_word_weighted = self.get_weighted(topic_id)
        phrase_list = tpr.extract_phrase(damping_factor=0.3, word_weighted_list=topic_word_weighted)
        phrase_list = phrase_list[0:n_phrases]

        return phrase_list

    def get_topic_phrase_by_sentence(self, comment_list, corpus, topic_id, n_phrases, with_score):
        phrase_list = self.get_topic_phrase_list_by_sentence(comment_list=comment_list, corpus=corpus, topic_id=topic_id, n_phrases=n_phrases)

        output = ""
        for item in phrase_list:
            phrase = item[0]
            score = item[2]
            if np.isnan(score):
                score = 0
            if with_score:
                output += f"{phrase} ({score:.03f}),"
            else:
                output += "%s, " % phrase
        return output

    def print_phrase_by_sentence(self, comment_list, corpus, n_phrase, with_score):
        leaf_node_id_list = []
        document_leaf_node_dict = self.hlda.document_leaves
        for node in document_leaf_node_dict:
            node_id = document_leaf_node_dict[node].node_id
            if node_id not in leaf_node_id_list:
                leaf_node_id_list.append(node_id)

        out = ""
        for node_id in leaf_node_id_list:
            out += f'topic={node_id} '
            out += self.get_topic_phrase_by_sentence(comment_list, corpus, node_id, n_phrase, with_score)
            print(out)
            out = ""

    def print_phrases_by_sentence(self, comment_list, corpus, n_phrase, with_score):
        topic_multi_document_by_sentence = self.get_topic_multi_document_by_sentence(comment_list=comment_list,
                                                                                     corpus=corpus)

        leaf_node_id_list = []
        document_leaf_node_dict = self.hlda.document_leaves
        for node in document_leaf_node_dict:
            node_id = document_leaf_node_dict[node].node_id
            if node_id not in leaf_node_id_list:
                leaf_node_id_list.append(node_id)

        for node_id in leaf_node_id_list:
            topic_document_list = []
            get_comment_list = []
            for comment_topic_by_sentence in topic_multi_document_by_sentence:
                comment_topic = []

                # コメントが持つトピックを調べる
                for sentence_topic in comment_topic_by_sentence:
                    sentence_topic_id = sentence_topic[1]
                    if sentence_topic_id not in comment_topic:
                        comment_topic.append(sentence_topic_id)

                # コメントが指定したトピックを持つ場合はリストに追加する
                if node_id in comment_topic:
                    get_comment_list.append(comment_topic_by_sentence)

            for comment in get_comment_list:
                for sentence in comment:
                    sentence_str = sentence[0]
                    sentence_topic_id = sentence[1]

                    if sentence_topic_id == node_id:
                        topic_document_list.append(sentence_str)

            # フレーズを抽出する
            tpr = TopicalPageRank(collection=topic_document_list, appear_tagging_list=["名詞", "形容詞"], w=10)
            topic_word_weighted = self.get_weighted(node_id)
            phrase_list = tpr.extract_phrase(damping_factor=0.3, word_weighted_list=topic_word_weighted)
            phrase_list = phrase_list[0:n_phrase]

            # フレーズが生成されていない観点を表示しない
            if len(phrase_list) == 0:
                continue

            output = f'topic={node_id} (documents={len(topic_document_list)}) '
            for item in phrase_list:
                phrase = item[0]
                score = item[2]
                if np.isnan(score):
                    score = 0
                if with_score:
                    output += f"{phrase} ({score:.03f}),"
                else:
                    output += "%s, " % phrase
            print(output)

    def get_topic_multi_document(self, comment_list, corpus):
        nlp = spacy.load("ja_ginza")
        topic_multi_document = []
        # ノードごとでの単語の重要度を取得
        leaf_node_id_list = []
        document_leaf_node_dict = self.hlda.document_leaves
        for node in document_leaf_node_dict:
            node_id = document_leaf_node_dict[node].node_id
            if node_id not in leaf_node_id_list:
                leaf_node_id_list.append(node_id)

        node_weight_list = []
        for node_id in leaf_node_id_list:
            word_weight = self.get_weighted(node_id)
            node_weight_list.append([node_id, word_weight])

        for comment in comment_list:
            # コメントを文単位に分割する(改修前）
            # replaced_comment = comment.replace("\r", "")
            # replaced_comment = replaced_comment.replace("。", "\n")
            # replaced_comment = replaced_comment.replace("？", "\n")
            # sentence_list = replaced_comment.split("\n")
            # sentence_list = [sentence for sentence in sentence_list if sentence]

            # コメントを文単位に分割する(改修後）
            replaced_comment = comment.replace("\r\n", "")
            doc = nlp(replaced_comment)
            sentence_list = [sent.text for sent in doc.sents]

            # 文章ごとにノードの選択&コメントが分類されるノードを保持
            comment_node_ratio = {}
            topic_word_count_dict = {}
            total_sentence_word_count = 0
            for sentence in sentence_list:
                topic_probability_list = np.zeros(len(node_weight_list))
                sentence_word_count = len(sentence)
                total_sentence_word_count += len(sentence)
                for i, item in enumerate(node_weight_list):
                    node_id = item[0]
                    node_weight = item[1]
                    if node_weight == 0:
                        continue

                    total_weight = 0
                    sentence_node_weight = 0
                    for word_weight in node_weight:
                        word = word_weight[0]
                        weight = word_weight[1]
                        # total_weight += weight
                        if word in sentence:
                            # 変更前
                            # word_appear_count = sentence.count(word)
                            # sentence_node_weight += weight * word_appear_count
                            # total_weight += weight * word_appear_count

                            # 変更後
                            sentence_node_weight += weight
                            total_weight += weight

                        else:
                            total_weight += weight
                    if total_weight != 0:
                        topic_probability_list[i] = np.round(sentence_node_weight / total_weight, 3)
                    else:
                        topic_probability_list[i] = 0
                index = topic_probability_list.argmax()
                node_id = node_weight_list[index][0]
                probability = topic_probability_list[index]
                if topic_word_count_dict.get(node_id) is None:
                    topic_word_count_dict[node_id] = sentence_word_count
                else:
                    topic_word_count_dict[node_id] += sentence_word_count

                if probability != 0:
                    if comment_node_ratio.get(node_id) is None:
                        comment_node_ratio[node_id] = 0

            for key, topic_word_count in topic_word_count_dict.items():
                topic_word_ratio = np.round(topic_word_count / total_sentence_word_count, 3)
                comment_node_ratio[key] = topic_word_ratio

            topic_multi_document.append([comment, comment_node_ratio])
        return topic_multi_document

    def print_topic_multi_document(self, comment_list, corpus, topic_id):
        topic_multi_document = self.get_topic_multi_document(comment_list=comment_list, corpus=corpus)

        print_comment_list = []
        for item in topic_multi_document:
            comment = item[0]
            comment_node_ratio = item[1]

            if comment_node_ratio.get(topic_id) is not None:
                print_comment_list.append([comment, comment_node_ratio[topic_id]])

            print_comment_list.sort(key=lambda x: x[1], reverse=True)

        for i, comment in enumerate(print_comment_list):
            comment_str = comment[0]
            topic_ratio = comment[1]
            comment_str = comment_str.replace("\r", "")
            comment_str = comment_str.replace("\n", "")
            print(f"No.{i+1}")
            print("「"+comment_str+"」")

    def get_topic_multi_document_by_sentence(self, comment_list, corpus):
        nlp = spacy.load("ja_ginza")
        topic_multi_document_by_sentence = []
        # ノードごとでの単語の重要度を取得
        leaf_node_id_list = []
        document_leaf_node_dict = self.hlda.document_leaves
        for node in document_leaf_node_dict:
            node_id = document_leaf_node_dict[node].node_id
            if node_id not in leaf_node_id_list:
                leaf_node_id_list.append(node_id)

        node_weight_list = []
        for node_id in leaf_node_id_list:
            word_weight = self.get_weighted(node_id)
            node_weight_list.append([node_id, word_weight])

        for comment in comment_list:
            comment_topic_by_sentence = []

            # コメントを文単位に分割する(改修前）
            # replaced_comment = comment.replace("\r", "")
            # replaced_comment = replaced_comment.replace("。", "\n")
            # replaced_comment = replaced_comment.replace("？", "\n")
            # sentence_list = replaced_comment.split("\n")
            # sentence_list = [sentence for sentence in sentence_list if sentence]

            # コメントを文単位に分割する(改修後）
            replaced_comment = comment.replace("\r\n", "")
            doc = nlp(replaced_comment)
            sentence_list = [sent.text for sent in doc.sents]

            # 文章ごとにノードの選択&コメントが分類されるノードを保持
            total_sentence_word_count = 0
            for sentence in sentence_list:
                topic_probability_list = np.zeros(len(node_weight_list))
                sentence_word_count = len(sentence)
                total_sentence_word_count += len(sentence)
                for i, item in enumerate(node_weight_list):
                    node_id = item[0]
                    node_weight = item[1]
                    if node_weight == 0:
                        continue

                    total_weight = 0
                    sentence_node_weight = 0
                    for word_weight in node_weight:
                        word = word_weight[0]
                        weight = word_weight[1]
                        # total_weight += weight
                        if word in sentence:
                            # 変更前
                            # word_appear_count = sentence.count(word)
                            # sentence_node_weight += weight * word_appear_count
                            # total_weight += weight * word_appear_count

                            # 変更後
                            sentence_node_weight += weight
                            total_weight += weight

                        else:
                            total_weight += weight
                    if total_weight != 0:
                        topic_probability_list[i] = np.round(sentence_node_weight / total_weight, 3)
                    else:
                        topic_probability_list[i] = 0
                index = topic_probability_list.argmax()
                node_id = node_weight_list[index][0]
                probability = topic_probability_list[index]

                if probability > 0.07:
                    comment_topic_by_sentence.append([sentence, node_id])
                else:
                    comment_topic_by_sentence.append([sentence, None])
            topic_multi_document_by_sentence.append(comment_topic_by_sentence)
        return topic_multi_document_by_sentence

    def print_topic_multi_document_by_sentence(self, comment_list, corpus, topic_id):
        topic_multi_document_by_sentence = self.get_topic_multi_document_by_sentence(comment_list=comment_list, corpus=corpus)

        print_comment_list = []
        for comment_topic_by_sentence in topic_multi_document_by_sentence:
            comment_topic = []

            # コメントが持つトピックを調べる
            for sentence_topic in comment_topic_by_sentence:
                sentence_topic_id = sentence_topic[1]
                if sentence_topic_id not in comment_topic:
                    comment_topic.append(sentence_topic_id)

            # コメントが指定したトピックを持つ場合は表示する
            if topic_id in comment_topic:
                print_comment_list.append(comment_topic_by_sentence)

        for i, comment in enumerate(print_comment_list):
            comment_str = ""
            for sentence in comment:
                sentence_str = sentence[0]
                sentence_topic_id = sentence[1]

                if sentence_topic_id == topic_id:
                    sentence_str = '\033[31m'+f'{sentence_str}'+'\033[0m'

                comment_str += sentence_str
            print(f"No.{i + 1}")
            print("「" + comment_str + "」")

    def print_topic_phrase_by_sentence(self, comment_list, corpus, topic_id):
        topic_multi_document_by_sentence = self.get_topic_multi_document_by_sentence(comment_list=comment_list, corpus=corpus)

        topic_comment_list = []
        get_comment_list = []
        for comment_topic_by_sentence in topic_multi_document_by_sentence:
            comment_topic = []

            # コメントが持つトピックを調べる
            for sentence_topic in comment_topic_by_sentence:
                sentence_topic_id = sentence_topic[1]
                if sentence_topic_id not in comment_topic:
                    comment_topic.append(sentence_topic_id)

            # コメントが指定したトピックを持つ場合は保管する
            if topic_id in comment_topic:
                get_comment_list.append(comment_topic_by_sentence)

        for comment in get_comment_list:
            for sentence in comment:
                sentence_str = sentence[0]
                sentence_topic_id = sentence[1]

                if sentence_topic_id == topic_id:
                    topic_comment_list.append(sentence_str)

        # フレーズを抽出する
        tpr = TopicalPageRank(collection=topic_comment_list, appear_tagging_list=["名詞", "形容詞"], w=10)
        topic_word_weighted = self.get_weighted(topic_id)
        phrase_list = tpr.extract_phrase(damping_factor=0.3, word_weighted_list=topic_word_weighted)

        print(phrase_list)

    def print_multi_node(self, comment_list, corpus, n_phrase, with_score):
        topic_multi_document = self.get_topic_multi_document(comment_list=comment_list, corpus=corpus)
        total_topic_id = []

        # 全体で出現するトピックのidを収集
        for item in topic_multi_document:
            topic_ratio = item[1]
            for topic_id, ratio in topic_ratio.items():
                if topic_id not in total_topic_id:
                    total_topic_id.append(topic_id)

        # トピックごとにまとめる
        for topic_id in total_topic_id:
            total_topic_documents = 0
            for item in topic_multi_document:
                topic_ratio = item[1]
                if topic_id in topic_ratio:
                    total_topic_documents += 1

            out = f'topic={topic_id} (documents={total_topic_documents}):'
            out += self.get_topic_phrase(comment_list, corpus, topic_id, n_phrase, with_score)
            print(out)

    def get_topic_by_sentence(self, comment_list, corpus, n_words=3):
        nlp = spacy.load("ja_ginza")
        topic_multi_document = []
        # ノードごとでの単語の重要度を取得
        leaf_node_id_list = []
        document_leaf_node_dict = self.hlda.document_leaves
        for node in document_leaf_node_dict:
            node_id = document_leaf_node_dict[node].node_id
            if node_id not in leaf_node_id_list:
                leaf_node_id_list.append(node_id)

        node_weight_list = []
        for node_id in leaf_node_id_list:
            word_weight = self.get_weighted(node_id)
            node_weight_list.append([node_id, word_weight])

        for comment in comment_list:
            # コメントを文単位に分割する(改修前）
            # replaced_comment = comment.replace("\r", "")
            # replaced_comment = replaced_comment.replace("。", "\n")
            # replaced_comment = replaced_comment.replace("？", "\n")
            # sentence_list = replaced_comment.split("\n")
            # sentence_list = [sentence for sentence in sentence_list if sentence]

            # コメントを文単位に分割する(改修後）
            replaced_comment = comment.replace("\r\n", "")
            doc = nlp(replaced_comment)
            sentence_list = [sent.text for sent in doc.sents]

            # 文章ごとにノードの選択&コメントが分類されるノードを保持
            for sentence_index, sentence in enumerate(sentence_list):
                topic_probability_list = np.zeros(len(node_weight_list))
                for i, item in enumerate(node_weight_list):
                    node_id = item[0]
                    node_weight = item[1]
                    if node_weight == 0:
                        continue

                    total_weight = 0
                    sentence_node_weight = 0
                    for word_weight in node_weight:
                        word = word_weight[0]
                        word_weight = word_weight[1]
                        # total_weight += weight
                        if word in sentence:
                            # 変更前
                            # word_appear_count = sentence.count(word)
                            # sentence_node_weight += word_weight * word_appear_count
                            # total_weight += word_weight * word_appear_count

                            # 変更後
                            sentence_node_weight += word_weight
                            total_weight += word_weight
                    else:
                            total_weight += word_weight
                    if total_weight != 0:
                        topic_probability_list[i] = np.round(sentence_node_weight / total_weight, 3)
                    else:
                        topic_probability_list[i] = 0

                # nodeの情報を取得する
                index = topic_probability_list.argmax()
                node_id = node_weight_list[index][0]
                probability = topic_probability_list[index]

                # node_weight = node_weight_list[index][:n_words]
                node_weight = node_weight_list[index][1][:n_words]
                node_words_str = ""
                for i, item in enumerate(node_weight):
                    node_words_str += f"{item[0]}({item[1]})"
                    if i != len(node_weight)-1:
                        node_words_str += ","

                print(f"{sentence_index}:{sentence}")
                print(f"node_id:{node_id}, node_words:{node_words_str}, probability:{probability}")
            print("------------------------------------------------------------------")

    def get_topic_one_sentence(self, sentence, corpus, n_words=3, node_id=1):
        topic_multi_document = []

        node_weight = self.get_weighted(node_id)
        if node_weight:
            total_weight = 0
            sentence_node_weight = 0
            print_str = ""
            for word_weight in node_weight[:n_words]:
                word = word_weight[0]
                word_weight = word_weight[1]

                if word in sentence:
                    # 変更前
                    # word_appear_count = sentence.count(word)
                    # sentence_node_weight += word_weight * word_appear_count
                    # total_weight += word_weight * word_appear_count

                    # 変更後
                    word_appear_count = sentence.count(word)
                    sentence_node_weight += word_weight
                    total_weight += word_weight
                    print_str += f"{word} (word_weight:{word_weight}) (word_appear_count{word_appear_count}), "
                else:
                    total_weight += word_weight
                    print_str += f"{word} (word_weight:{word_weight}) (word_appear_count{0}), "

                if total_weight != 0:
                    topic_probability = np.round(sentence_node_weight / total_weight, 3)
                else:
                    topic_probability = 0

                # node_weight = node_weight_list[index][:n_words]
                node_weight = node_weight[:n_words]
                node_words_str = ""
                for i, item in enumerate(node_weight):
                    node_words_str += f"{item[0]}({item[1]})"
                    if i != len(node_weight) - 1:
                        node_words_str += ","

            print(f"sentence:{sentence}")
            print(f"node_id:{node_id}, node_words:{node_words_str}, probability:{topic_probability}")
            print(f"各単語の出現回数:{print_str}")
            print("------------------------------------------------------------------")

    def get_topic_one_sentence_with_color(self, sentence, corpus, n_words=3, node_id=1):
        # 指定したノードの単語の重みを取得する
        node_weight = self.get_weighted(node_id)

        if node_weight:
            # 文に対して分かち書きを行う
            wd = WordDividerMecab()

            if len(sentence) > 0:
                text = wd.wakati_text(text=sentence)

            text = text.split(" ")

            sentence_with_color = ""
            word_weight_word_list = [word_weight[0] for word_weight in node_weight if word_weight[1] > 0]
            for word in text:
                if word in word_weight_word_list:
                    sentence_with_color += '\033[31m'+f'{word}'+'\033[0m'
                else:
                    sentence_with_color += word

            total_weight = 0
            sentence_node_weight = 0
            print_str = ""
            for word_weight in node_weight[:n_words]:
                word = word_weight[0]
                word_weight = word_weight[1]

                if word in sentence:
                    # 変更前
                    # word_appear_count = sentence.count(word)
                    # sentence_node_weight += word_weight * word_appear_count
                    # total_weight += word_weight * word_appear_count

                    # 変更後
                    word_appear_count = sentence.count(word)
                    sentence_node_weight += word_weight
                    total_weight += word_weight
                    print_str += f"{word} (word_weight:{word_weight}) (word_appear_count{word_appear_count}), "
                else:
                    total_weight += word_weight
                    print_str += f"{word} (word_weight:{word_weight}) (word_appear_count{0}), "

                if total_weight != 0:
                    topic_probability = np.round(sentence_node_weight / total_weight, 3)
                else:
                    topic_probability = 0

                # node_weight = node_weight_list[index][:n_words]
                node_weight = node_weight[:n_words]
                node_words_str = ""
                for i, item in enumerate(node_weight):
                    node_words_str += f"{item[0]}({item[1]})"
                    if i != len(node_weight) - 1:
                        node_words_str += ","

            print(f"sentence:{sentence_with_color}")
            print(f"node_id:{node_id}, node_words:{node_words_str}")
            print(f"probability:{topic_probability}")
            print(f"各単語の出現回数:{print_str}")
            print("------------------------------------------------------------------")

    def get_topic_with_color(self, comment_list, corpus, n_words=3):
        nlp = spacy.load("ja_ginza")
        topic_multi_document = []
        # ノードごとでの単語の重要度を取得
        leaf_node_id_list = []
        document_leaf_node_dict = self.hlda.document_leaves
        for node in document_leaf_node_dict:
            node_id = document_leaf_node_dict[node].node_id
            if node_id not in leaf_node_id_list:
                leaf_node_id_list.append(node_id)

        node_weight_list = []
        for node_id in leaf_node_id_list:
            word_weight = self.get_weighted(node_id)
            node_weight_list.append([node_id, word_weight])

        for comment in comment_list:
            # コメントを文単位に分割する(改修前）
            # replaced_comment = comment.replace("\r", "")
            # replaced_comment = replaced_comment.replace("。", "\n")
            # replaced_comment = replaced_comment.replace("？", "\n")
            # sentence_list = replaced_comment.split("\n")
            # sentence_list = [sentence for sentence in sentence_list if sentence]

            # コメントを文単位に分割する(改修後）
            replaced_comment = comment.replace("\r\n", "")
            doc = nlp(replaced_comment)
            sentence_list = [sent.text for sent in doc.sents]

            # 文章ごとにノードの選択&コメントが分類されるノードを保持
            for sentence_index, sentence in enumerate(sentence_list):
                topic_probability_list = np.zeros(len(node_weight_list))
                for i, item in enumerate(node_weight_list):
                    node_id = item[0]
                    node_weight = item[1]
                    if node_weight == 0:
                        continue

                    total_weight = 0
                    sentence_node_weight = 0
                    for word_weight in node_weight:
                        word = word_weight[0]
                        word_weight = word_weight[1]
                        # total_weight += weight
                        if word in sentence:
                            word_appear_count = sentence.count(word)
                            sentence_node_weight += word_weight * word_appear_count
                            total_weight += word_weight * word_appear_count
                        else:
                            total_weight += word_weight
                    if total_weight != 0:
                        topic_probability_list[i] = np.round(sentence_node_weight / total_weight, 3)
                    else:
                        topic_probability_list[i] = 0

                # nodeの情報を取得する
                index = topic_probability_list.argmax()
                node_id = node_weight_list[index][0]
                probability = topic_probability_list[index]

                # node_weight = node_weight_list[index][:n_words]
                node_weight = node_weight_list[index][1][:n_words]
                node_words_str = ""
                for i, item in enumerate(node_weight):
                    node_words_str += f"{item[0]}({item[1]})"
                    if i != len(node_weight)-1:
                        node_words_str += ","

                # 文に対して分かち書きを行う
                wd = WordDividerMecab()

                if len(sentence) > 0:
                    text = wd.wakati_text(text=sentence)

                    text = text.split(" ")

                    sentence_with_color = ""
                    word_weight_word_list = [word_weight[0] for word_weight in node_weight if word_weight[1] > 0]
                    for word in text:
                        if word in word_weight_word_list:
                            sentence_with_color += '\033[31m' + f'{word}' + '\033[0m'
                        else:
                            sentence_with_color += word

                print(f"{sentence_index}:{sentence_with_color}")
                print(f"node_id:{node_id}, node_words:{node_words_str}, probability:{probability}")
            print("------------------------------------------------------------------")

    def get_multi_topic_with_color(self, comment_list, corpus, n_words=3):
        nlp = spacy.load("ja_ginza")
        topic_multi_document = []
        # ノードごとでの単語の重要度を取得
        leaf_node_id_list = []
        document_leaf_node_dict = self.hlda.document_leaves
        for node in document_leaf_node_dict:
            node_id = document_leaf_node_dict[node].node_id
            if node_id not in leaf_node_id_list:
                leaf_node_id_list.append(node_id)

        node_weight_list = []
        for node_id in leaf_node_id_list:
            word_weight = self.get_weighted(node_id)
            node_weight_list.append([node_id, word_weight])

        for comment in comment_list:
            # コメントを文単位に分割する(改修前）
            # replaced_comment = comment.replace("\r", "")
            # replaced_comment = replaced_comment.replace("。", "\n")
            # replaced_comment = replaced_comment.replace("？", "\n")
            # sentence_list = replaced_comment.split("\n")
            # sentence_list = [sentence for sentence in sentence_list if sentence]

            # コメントを文単位に分割する(改修後）
            replaced_comment = comment.replace("\r\n", "")
            doc = nlp(replaced_comment)
            sentence_list = [sent.text for sent in doc.sents]

            # 文章ごとにノードの選択&コメントが分類されるノードを保持
            for sentence_index, sentence in enumerate(sentence_list):
                print(f"{sentence_index}:{sentence}")
                topic_probability_list = np.zeros(len(node_weight_list))
                for i, item in enumerate(node_weight_list):
                    node_id = item[0]
                    node_weight = item[1]
                    if node_weight == 0:
                        continue

                    total_weight = 0
                    sentence_node_weight = 0
                    for word_weight in node_weight:
                        word = word_weight[0]
                        word_weight = word_weight[1]
                        # total_weight += weight
                        if word in sentence:
                            word_appear_count = sentence.count(word)
                            sentence_node_weight += word_weight * word_appear_count
                            total_weight += word_weight * word_appear_count
                        else:
                            total_weight += word_weight
                    if total_weight != 0:
                        topic_probability_list[i] = np.round(sentence_node_weight / total_weight, 3)
                    else:
                        topic_probability_list[i] = 0

                # nodeの情報を取得する(上位3つ）
                node_rank_list = []
                for i in range(3):
                    index = topic_probability_list.argmax()
                    node_id = node_weight_list[index][0]
                    probability = topic_probability_list[index]
                    topic_probability_list[index] = 0 #値を取得したら0にする
                    node_rank_list.append([node_id, probability])

                # 文に対して分かち書きを行う
                wd = WordDividerMecab()

                if len(sentence) > 0:
                    text = wd.wakati_text(text=sentence)

                    text = text.split(" ")

                    for index, node in enumerate(node_rank_list):
                        node_index = node[0]
                        node_probability = node[1]

                        sentence_with_color = ""
                        word_weight_word_list = [word_weight[0] for word_weight in node_weight_list[node_index][1] if word_weight[1] > 0]
                        for word in text:
                            if word in word_weight_word_list:
                                sentence_with_color += '\033[31m' + f'{word}' + '\033[0m'
                            else:
                                sentence_with_color += word

                        # node_weight = node_weight_list[index][:n_words]

                        node_weight = node_weight_list[node_index][1][:n_words]
                        node_words_str = ""
                        for i, item in enumerate(node_weight):
                            node_words_str += f"{item[0]}({item[1]})"
                            if i != len(node_weight) - 1:
                                node_words_str += ","

                    print(f"{index+1}位:{sentence_with_color}")
                    print(f"node_id:{node_id}, node_words:{node_words_str}, probability:{probability}")
            print("------------------------------------------------------------------")

def main():
    expand_hlda = ExpandHldaModel(pickle_path='pickle/2022_11_12/yahoo_hlda_2022_11_12.pickle')
    # expand_hlda.hlda.print_nodes(n_words = 10, with_weights = False)

if __name__ == '__main__':
        main()




