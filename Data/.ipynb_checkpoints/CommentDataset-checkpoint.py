import sys
sys.path.append('../NLP')

from MyNLP import WordDividerMecab
from sklearn.feature_extraction.text import TfidfVectorizer


class CommentDataset:
    def __init__(self, comment_list):
        if not isinstance(comment_list, list):
            raise TypeError("コンストラクタにはlistを指定してください。")
        
        self.comment_list = comment_list
    
    def delete_comment_specified_string(self, min_chars_num, max_chars_num = 1000):
        formatted_comment_list = []
        
        for text in self.comment_list:
            if len(text) > min_chars_num and len(text) < max_chars_num:
                formatted_comment_list.append(text)
                
        self.comment_list = formatted_comment_list
    
    def get_appeared_word_list(self):
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(self.comment_list)
        self.voc = sorted(vectorizer.vocabulary_)
        
    def formatted_word_segmentation(self):
        formatted_comment_list = []
        wd = WordDividerMecab()
        stop_word_list = ["まだ", "ある", "なる", "なる", "する", "し", "する", "いる", "なっ", "せ", "い", "やる", "ない"]
        
        for text in self.comment_list:
            if len(text) > 0:
                text = wd.wakati_text_only_nouns(text=text, stop_word_list=stop_word_list)
                formatted_comment_list.append(text)
                
        self.comment_list = formatted_comment_list
        
    def formatted_input_hlda(self):
        self.formatted_word_segmentation()
        self.get_appeared_word_list()

        corpus = []

        for comment in self.comment_list:
            list = comment.split(" ")
            corpus.append(list)
            filtered_corpus = []
            for comment in corpus:
                filtered_comment = []
                for word in comment:
                    if word in self.voc:
                        filtered_comment.append(word)
                filtered_corpus.append(filtered_comment)

        corpus = filtered_corpus
        corpus = [comment for comment in corpus if len(comment) != 0]

        vocab_index = {}

        for i, w in enumerate(self.voc):
            vocab_index[w] = i

        new_corpus = []

        corpus = [comment for comment in corpus if comment != '']

        for sentence in corpus:
            new_sentence = []
            for word in sentence:
                word_idx = vocab_index[word]
                new_sentence.append(word_idx)
            new_corpus.append(new_sentence)
        self.comment_list = new_corpus

def main():
    list = ['今日は天気がいいですね', '明日は雨ですかね？']
    comment_dataset = CommentDataset(comment_list=list)

    comment_dataset.formatted_word_segmentation()
    print(comment_dataset.comment_list)

if __name__ == '__main__':
        main()