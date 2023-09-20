import csv
import spacy

# 人が指定するところ
read_file_path = "/home/kawai/デスクトップ/プログラム/TechnicalInvestigation/Data/yahoo/2023_06_27/20230627_mynumbercard_untenmenkyosyou.csv"
csv_file_name = "20230627_mynumbercard_untenmenkyosyou.csv"
csv_file_path = "CSV/" + csv_file_name
comment_count = 100

# 対象とするファイルを読み込む
yahoo_news_total_comments = []
with open(read_file_path, encoding="cp932") as f:
    reader = csv.reader(f)
    header = next(reader)

    for row in reader:
        yahoo_news_total_comments.append(row)

# 変更したい内容で新たに書き込む
nlp = spacy.load("ja_ginza")

with open(csv_file_path, 'w', newline='') as csv_file:
    fieldnames = ['文', '出現順序', '全体のコメント', 'ラベル']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for comment in yahoo_news_total_comments[:comment_count]:
        # コメントを文単位で区切る
        comment = comment[0]
        replaced_comment = comment.replace("\r\n", "")
        doc = nlp(replaced_comment)
        sentence_list = [sent.text for sent in doc.sents if len(sent.text) != 1]

        # 文ごとにCSVファイルに書き込む
        for index, sentence in enumerate(sentence_list):
            print(f"{index}:{sentence}:{len(sentence)}")
            try:
                writer.writerow({'文': sentence, '出現順序': index + 1, '全体のコメント': comment})
            except UnicodeEncodeError:
                continue
