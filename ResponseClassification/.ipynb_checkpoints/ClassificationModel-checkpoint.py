import numpy as np
import pandas as pd
import MeCab

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import PassiveAggressiveClassifier

count = CountVectorizer()
df = pd.read_csv("./data.csv", encoding="cp932")

# 欠測値の削除
df = df.dropna()
df = df.loc[:, "comment_sentence":"label"]
x, y = df.loc[:, "comment_sentence"].values, df.loc[:, "label"].values
print(df.head())
print(x, y)
