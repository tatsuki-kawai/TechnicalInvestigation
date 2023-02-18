import psycopg2

from Object import Data
from Preprocessing import Preprocessing


class TweetDatabasePsycopg2:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="localhost",
            database="tweetdb",
            user="tatsuki",
            password="kawaistars"
        )
        self.cur = self.connection.cursor()

    def insert_opinion_tweet(self, tweet_id, user_id, created_at, opinion_type, search_query, text):
        # data = (tweet_id, created_at, text, irony)
        # self.cur.execute('INSERT INTO tweet VALUES(%s, %s, %s, %s)', data)

        # テキストの前処理
        text = text.replace("\n", "\\n")
        # text = re.sub("http.+", "", text)
        # text = re.sub("@.+ ", "", text)

        sql = f'INSERT INTO opinion (tweet_id, user_id, created_at, opinion_type, search_query, text) ' \
              f'VALUES(%s, %s, %s, %s, %s, %s)'
        data = (tweet_id, user_id, created_at, opinion_type, search_query, text)
        self.cur.execute(sql, data)
        # print(self.cur.query)
        self.connection.commit()

    def get_opinion_id(self, tweet_id):
        result = None
        sql = f"SELECT * FROM opinion WHERE tweet_id = {tweet_id}"
        self.cur.execute(sql)
        opinion_tweet = self.cur.fetchone()
        self.connection.commit()
        if opinion_tweet is not None:
            result = opinion_tweet[0]
        return result

    def get_all_opinion_tweet(self):
        sql = f"SELECT * FROM opinion"
        self.cur.execute(sql)
        opinion_tweet_list = self.cur.fetchall()
        self.connection.commit()
        return opinion_tweet_list

    def get_opinion_tweet(self, id):
        sql = f"SELECT * FROM opinion WHERE id = {id}"
        self.cur.execute(sql)
        opinion_tweet = self.cur.fetchone()
        self.connection.commit()
        return opinion_tweet

    def get_all_not_opinion_tweet(self):
        sql = f"SELECT * FROM not_opinion"
        self.cur.execute(sql)
        not_opinion_tweet_list = self.cur.fetchall()
        self.connection.commit()
        return not_opinion_tweet_list

    def insert_not_opinion_tweet(self, tweet_id, user_id, created_at, search_query, text):
        # data = (tweet_id, created_at, text, irony)
        # self.cur.execute('INSERT INTO tweet VALUES(%s, %s, %s, %s)', data)

        # テキストの前処理
        text = text.replace("\n", "\\n")
        # text = re.sub("http.+", "", text)
        # text = re.sub("@.+ ", "", text)

        sql = f'INSERT INTO not_opinion (tweet_id, user_id, created_at, search_query, text) ' \
              f'VALUES(%s, %s, %s, %s, %s)'
        data = (tweet_id, user_id, created_at, search_query, text)
        self.cur.execute(sql, data)
        # print(self.cur.query)
        self.connection.commit()

    def insert_comment_tweet(self, tweet_id, opinion_tweet_id, user_id, comment_type, created_at, text):
        # data = (tweet_id, created_at, text, irony)
        # self.cur.execute('INSERT INTO tweet VALUES(%s, %s, %s, %s)', data)

        # テキストの前処理
        text = text.replace("\n", "\\n")
        # text = re.sub("https.+", "", text)
        # text = re.sub("@.+ ", "", text)

        sql = f'INSERT INTO comment (tweet_id, opinion_tweet_id, user_id, comment_type, created_at, text) ' \
              f'VALUES(%s, %s, %s, %s, %s, %s)'
        data = (tweet_id, opinion_tweet_id, user_id, comment_type, created_at, text)
        self.cur.execute(sql, data)
        # print(self.cur.query)
        self.connection.commit()

    def get_comment(self, id):
        url = None
        sql = f"SELECT * FROM comment WHERE id = {id}"
        self.cur.execute(sql)
        comment_tweet = self.cur.fetchone()
        return comment_tweet

    def get_comment_url(self, id):
        url = None
        sql = f"SELECT * FROM comment WHERE id = {id}"
        self.cur.execute(sql)
        comment_tweet = self.cur.fetchone()
        if comment_tweet is not None:
            url = f'https://twitter.com/{comment_tweet[2]}/status/{comment_tweet[1]}'
        return url

    def join_opinion_comment(self):
        sql = f"SELECT opinion.id AS opinion_id, comment.id AS comment_id, opinion.tweet_id AS opinion_tweet_id, " \
              f"comment.tweet_id AS comment_tweet_id, opinion.text AS opinion_text, comment.text AS comment_text " \
              f"FROM comment JOIN opinion ON comment.opinion_tweet_id = opinion.id"
        self.cur.execute(sql)
        lines = self.cur.fetchall()
        return lines

    def insert_data(self, data_without_label):
        # data = (tweet_id, created_at, text, irony)
        # self.cur.execute('INSERT INTO tweet VALUES(%s, %s, %s, %s)', data)

        sql = f'INSERT INTO data (opinion_id, comment_id, opinion_tweet_id, comment_tweet_id, number, opinion_text, ' \
              f'comment_sentence, label) ' \
              f'VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
        data = (data_without_label.opinion_id, data_without_label.comment_id, data_without_label.opinion_tweet_id,
                data_without_label.comment_tweet_id, data_without_label.number, data_without_label.opinion_text,
                data_without_label.comment_sentence, data_without_label.label)
        self.cur.execute(sql, data)
        # print(self.cur.query)
        self.connection.commit()

    def get_all_data(self):
        sql = f"SELECT * FROM data"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def get_data_from_comment_tweet_id(self, comment_tweet_id, number):
        sql = f"SELECT * FROM data WHERE comment_tweet_id = {comment_tweet_id} AND number = {number}"
        self.cur.execute(sql)
        result = self.cur.fetchone()
        return result

    def get_data_without_label(self, opinion_type=0):
        sql = f"SELECT * FROM data " \
              f"WHERE opinion_id not in (SELECT opinion_id FROM data WHERE label is not null) " \
              f"AND opinion_id in (SELECT id FROM opinion WHERE opinion_type = {opinion_type})"
        self.cur.execute(sql)
        lines = self.cur.fetchall()
        # print(self.cur.query)
        return lines

    def update_data(self, data_id, label):
        sql = f"UPDATE data SET label = {label} WHERE id = {data_id}"
        self.cur.execute(sql)
        print(self.cur.query)
        self.connection.commit()

    # def select_tweet(self):
    #     # self.cur.execute('SELECT * FROM tweet')
    #
    #     sql = f'SELECT * FROM {self.name}'
    #     self.cur.execute(sql)
    #     result = self.cur.fetchall()
    #
    #     for tweet in result:
    #         print(tweet)
    #
    # def select_count_tweet(self):
    #     # self.cur.execute('SELECT COUNT(*) FROM tweet')
    #
    #     sql = f'SELECT COUNT(*) FROM {self.name}'
    #     self.cur.execute(sql)
    #     print(self.cur.fetchone())
    #     self.connection.commit()
    #
    # def delete_tweet(self):
    #     # self.cur.execute('DELETE FROM tweet')
    #
    #     sql = f'DELETE FROM {self.name}'
    #     self.cur.execute(sql)
    #     self.connection.commit()
    #
    # def delete_a_tweet(self, tweet_id):
    #     # self.cur.execute('DELETE FROM tweet WHERE id = %s', (tweet_id,))
    #
    #     sql = f'DELETE FROM {self.name} WHERE id = %s'
    #     self.cur.execute(sql, (tweet_id,))
    #     self.connection.commit()

# tweetdb = TweetDatabasePsycopg2()
# print(tweetdb.get_comment_url(355))



