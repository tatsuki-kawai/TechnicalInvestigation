import sys
sys.path.append('../GenerateLabel')

import pickle
import gzip
import numpy as np
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

    def get_topic_multi_document(self, comment_list, corpus):
        separators = "。.? "
        result = []
        for comment in corpus:
            comment = comment.replace("\n", " ")
            sentence_list = comment.split(separators)

            class_list = []
            leaf_node_list = []
            document_leaf_node_list = self.hlda.document_leaves
            for node in document_leaf_node_list:
                if node not in leaf_node_list:
                    leaf_node_list.append(node)

            node_weight_list = []
            for node in leaf_node_list:
                node_id = node.node_id
                word_weight = self.get_weighted(node_id)
                node_weight_list.append([node_id, word_weight])

            for sentence in sentence_list:
                print(sentence)




            # result.append([comment, class_list])


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

    def get_topic_phrase(self, comment_list, corpus, topic_id, n_phrases, with_score):
        topic_document_list = self.get_topic_document(comment_list=comment_list, corpus=corpus,
                                                      topic_id=topic_id)
        tpr = TopicalPageRank(collection=topic_document_list, appear_tagging_list=["名詞", "形容詞"], w=10)
        topic_word_weighted = self.get_weighted(topic_id)
        phrase_list = tpr.extract_phrase(damping_factor=0.3, word_weighted_list=topic_word_weighted)
        phrase_list = phrase_list[0:n_phrases]

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
        out += 'topic=%d level=%d (documents=%d): ' % (node.node_id, node.level, node.customers)
        out += self.get_topic_phrase(comment_list, corpus, node.node_id, n_phrase, with_score)
        print(out)
        for child in node.children:
            self.print_phrase(child, indent + 1, comment_list, corpus, n_phrase, with_score)


def main():
    expand_hlda = ExpandHldaModel(pickle_path='pickle/2022_11_12/yahoo_hlda_2022_11_12.pickle')
    # expand_hlda.hlda.print_nodes(n_words = 10, with_weights = False)

if __name__ == '__main__':
        main()




