import numpy as np
import pandas as pd
import janome
import matplotlib.pyplot as plt
from janome.tokenizer import Tokenizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.model_selection import learning_curve
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, classification_report
from imblearn.under_sampling import RandomUnderSampler

class WordDivider:
    def __init__(self):
        self.wakati = Tokenizer(wakati=True)
        self.t = Tokenizer()

    def wakati_words(self, text):
        if not text:
            return []

        words = []
        text = list(self.wakati.tokenize(text))
        for word in text:
            words.append(word)

        return words

    def surface_words(self, text):
        if not text:
            return []

        words = []
        for token in self.t.tokenize(text):
            words.append(token.base_form)
        return words

    def wakati_text(self, text):
        if not text:
            return []

        words = []
        wakati = list(self.wakati.tokenize(text))
        for word in wakati:
            words.append(word)

        output = ""
        for word in words:
            output += word
            output += " "
        return output

count = CountVectorizer()
df = pd.read_csv("./data.csv", encoding="cp932")

# 欠測値の削除
df = df.dropna()
df = df.loc[:, "comment_sentence":"label"]
# print(df["label"].unique())
df = df.replace({"label": {170: 6, 0: 6, 1: 6, 2: 6, 5: 6}})

# 訓練データを通常文とツイート行為の否定(3,4)に分ける
df = df.replace({"label": {6: 0, 3: 1, 4: 1}})

wd = WordDivider()
# 訓練データとテストデータの分割
train, test = train_test_split(df, test_size=0.25, stratify=df["label"].values)
print(train["label"].value_counts())
x_train, y_train = train.loc[:, "comment_sentence"].tolist(), train.loc[:, "label"].tolist()
x_test, y_test = test.loc[:, "comment_sentence"].tolist(), test.loc[:, "label"].tolist()
x_train = [wd.wakati_text(text) for text in x_train]
x_test = [wd.wakati_text(text) for text in x_test]