import pickle
import gzip
import numpy as np
from hlda.sampler import HierarchicalLDA

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
    
    def print_nodes(self, words, weights):
        self.hlda.print_nodes(n_words = words, with_weights = weights)

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
            print(f"No.{i}")
            print(document)
            print("\n")

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


def main():
    expand_hlda = ExpandHldaModel(pickle_path='pickle/2022_11_12/yahoo_hlda_2022_11_12.pickle')
    # expand_hlda.hlda.print_nodes(n_words = 10, with_weights = False)

if __name__ == '__main__':
        main()




