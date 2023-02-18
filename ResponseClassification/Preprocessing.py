import demoji
import spacy
import re
import functools

from ja_sentence_segmenter.common.pipeline import make_pipeline
from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation

class Preprocessing:
    def tweet_preprocessing(self, text):
        text = text.replace("\\n", "\n")
        text = text.replace("\n", "")
        text = re.sub("http.+", "", text)
        text = re.sub("@[0-9a-zA-Z_]{1,15}\s", "", text)
        return text

    def delete_emoji(self, text):
        replace = demoji.replace(string=text, repl="")
        return replace

    def trans_newline(self, text):
        sents = []
        nlp = spacy.load('ja_ginza')
        doc = nlp(text)
        for sent in doc.sents:
            text = sent.text
            sents.append(text)
        return sents

    def segment_splitter(self, text):
        split_punc2 = functools.partial(split_punctuation, punctuations=r"。!?")
        segmenter = make_pipeline(normalize, split_newline, split_punc2)
        sents = segmenter(text)
        return sents

    def test_preprocessing(self, text):
        text = self.tweet_preprocessing(text)
        text = self.delete_emoji(text)
        sents = self.trans_newline(text)
        # sents = self.segment_splitter(text)
        for sent in sents:
            print(sent)

    def preprocessing(self, text):
        text = self.tweet_preprocessing(text)
        text = self.delete_emoji(text)
        sents = self.trans_newline(text)
        for sent in sents:
            print(sent)
