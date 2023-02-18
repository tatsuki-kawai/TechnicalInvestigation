import tweepy
import time
import random
import json
import csv
import re
import glob
import os
import pandas as pd
from datetime import datetime
from datetime import timedelta
import MorphologicalAnalysis
from mlask import MLAsk
import MeCab

import TweetDB


class TweetSearcher:
    def __init__(self, dic_type=MorphologicalAnalysis.Takamura_Dic):
        self.analyst = MorphologicalAnalysis.Analyst()
        self.timeline_count = 50

        # 認証に必要なキーとトークン
        api_key = 'HtMhGGAMfDYWN5fvZKXBoN5H1'
        api_secret = 'MWvyNG71Qx1e64bCALp9lw6xSpjgSEIfDtBYFiW6GVUbkzD1Uz'
        access_token = '1016472223278755840-eLir0PqXd9sQFbEyLbfCOYAa0Sa1xZ'
        access_token_secret = 'wnltONp3gabXGG230lqgYgPvCLYtOdaPVjEYoYCuzsO78'

        # APIの認証
        self.auth = tweepy.OAuthHandler(api_key, api_secret)
        self.auth.set_access_token(access_token, access_token_secret)

        # APIインスタンスの生成
        self.api = tweepy.API(self.auth)

    def get_api(self):
        return self.api

    def search_users(self, user_name, user_screen_name):
        target_user = None
        users = self.api.search_users(q=user_screen_name)

        for user_candidate in users:
            if user_candidate.name == user_name:
                target_user = user_candidate

        return target_user

    def get_user(self, user_screen_name):
        target_user = self.api.get_user(screen_name=user_screen_name)
        return target_user

    def get_user_from_id(self, user_id):
        try:
            target_user = self.api.get_user(user_id=user_id)
        except tweepy.errors.NotFound:
            target_user = None
        return target_user

    def old_get_tweet(self, user_id, tweet_created_at):
        target_tweet = {}

        # 指定したユーザのタイムラインの取得
        results = self.api.user_timeline(user_id=user_id, count=self.timeline_count)

        # 指定した作成日時(string)をdatetimeに変換
        tweet_created_at = datetime.strptime(tweet_created_at, '%Y-%m-%d %H:%M')

        for result in results:
            sub = tweet_created_at - result.created_at
            delta1 = timedelta(days=0, seconds=0, minutes=59, hours=8)
            delta2 = timedelta(days=0, seconds=0, minutes=0, hours=9)

            if delta1 < sub < delta2:
                target_tweet = result

        return target_tweet

    def search_tweet_list(self, query, max_count):
        tweet_list = []
        tweets = self.api.search_tweets(q=f"{query}", count=max_count, tweet_mode="extended")
        for tweet in tweets:
            tweet_list.append(tweet)
        return tweet_list

    def get_tweet(self, screen_name, tweet_id):
        target_tweet = None

        # 指定したユーザのタイムラインの取得
        target_user = self.get_user(user_screen_name=screen_name)
        results = self.api.user_timeline(user_id=target_user.id, count=self.timeline_count, tweet_mode="extended")

        # 取得したタイムラインから目的のツイートを取得する
        for result in results:
            if result.id == tweet_id:
                target_tweet = result

        return target_tweet

    def get_tweet_from_url(self, url):
        # URLから関係のある情報を取得する
        related_words = self.split_url(url)
        screen_name = related_words[0]
        tweet_id = int(related_words[1])

        # get_tweetメソッドで目的のツイートを取得する
        target_tweet = self.get_tweet(screen_name=screen_name, tweet_id=tweet_id)
        if target_tweet is None:
            print('ツイートを取得できませんでした')
        return target_tweet

    def get_url(self, screen_name, tweet_id):
        try:
            url = f'URL:https://twitter.com/{screen_name}/status/{tweet_id}'
        except AttributeError:
            url = "ツイートが消されています"
        return url

    def get_reply(self, original_tweet, max_count):
        target_replys = []
        screen_name = original_tweet.user.screen_name
        tweets = self.api.search_tweets(q=f'@{screen_name} exclude:retweets', count=max_count, tweet_mode="extended")
        for tweet in tweets:
            if original_tweet.id == tweet.in_reply_to_status_id:
                target_replys.append(tweet)
        return target_replys

    def get_quoted_retweet(self, original_tweet, max_count):
        target_quoted_retweet = []
        url = f'https://twitter.com/{original_tweet.user.screen_name}/status/{original_tweet.id}'
        tweets = self.api.search_tweets(q=url, count=max_count, tweet_mode="extended")
        for tweet in tweets:
            try:
                if original_tweet.id == tweet.quoted_status_id:
                    target_quoted_retweet.append(tweet)
            except AttributeError:
                continue

        return target_quoted_retweet

    def calculate_tweet_sentiment_score(self, sentence_list):
        for sentence in sentence_list:
            sentiment_score = self.analyst.calc_pos_neg_score(sentence.text)
            print('----------------------------')
            print(f'URL:https://twitter.com/{sentence.user.screen_name}/status/{sentence.id}')
            print(f'text:{sentence.text}')
            print(f'reply_score:{sentiment_score}')

    def inside_calc_sentiment_score(self, sentence_list):
        for sentence in sentence_list:
            print('----------------------------')
            self.analyst.inside_calc_pos_neg_score(sentence.text)

    def classifier_pos_neg_sentence(self, sentence_list):
        # pn分類用のリストを定義
        pos_sentence_list = []
        neg_sentence_list = []
        for sentence in sentence_list:
            sentiment_score = self.analyst.calc_pos_neg_score(sentence.text)
            # pnを分類分けする
            if sentiment_score >= 0:
                pos_sentence_list.append(sentence)
            else:
                neg_sentence_list.append(sentence)
        return pos_sentence_list, neg_sentence_list

    def get_comment(self, original_tweet, max_count=100):
        replys = self.get_reply(original_tweet=original_tweet, max_count=max_count)
        quoted_retweets = self.get_quoted_retweet(original_tweet=original_tweet, max_count=max_count)

        reply_sentence = []
        quoted_retweet_sentence = []

        if len(replys) != 0:
            for reply in replys:
                reply_sentence.append(reply.full_text)

        if len(quoted_retweets) != 0:
            for quoted_retweet in quoted_retweets:
                quoted_retweet_sentence.append(quoted_retweet.full_text)

        return reply_sentence, quoted_retweet_sentence

    def get_comment_tweet(self, original_tweet, max_count=100):
        replys = self.get_reply(original_tweet=original_tweet, max_count=max_count)
        quoted_retweets = self.get_quoted_retweet(original_tweet=original_tweet, max_count=max_count)

        return replys, quoted_retweets

    def get_comment_ambience(self, original_tweet, max_count=50):
        replys = self.get_reply(original_tweet=original_tweet, max_count=max_count)
        quoted_retweets = self.get_quoted_retweet(original_tweet=original_tweet, max_count=max_count)
        reply_ambience = 0
        quoted_retweet_ambience = 0

        if len(replys) != 0:
            reply_sentence = []
            for reply in replys:
                reply_sentence.append(reply.full_text)
            reply_ambience = self.analyst.calc_pos_neg_ambience_score(sentence_list=reply_sentence)

        if len(quoted_retweets) != 0:
            quoted_retweet_sentence = []
            for quoted_retweet in quoted_retweets:
                quoted_retweet_sentence.append(quoted_retweet.full_text)
            quoted_retweet_ambience = self.analyst.calc_pos_neg_ambience_score(sentence_list=quoted_retweet_sentence)

        return reply_ambience, quoted_retweet_ambience

    def search_buz_tweet(self, count):
        buz_tweet_list = self.api.search_tweets(q='min_replies:10 min_retweets:500', lang='ja', count=count, tweet_mode="extended")
        for buz_tweet in buz_tweet_list:
            self.print_detailed_tweet_info(buz_tweet)
            limit_late = self.get_friendship_show_limit()
            print(f'limit_rate:{limit_late}')
            if limit_late < 20:
                time.sleep(60 * 15)
            self.count_follower_retweets(buz_tweet)

        print(f'{len(buz_tweet_list)}件のツイートを表示しました')

    def search_damaged_buz_tweet(self, query='', min_replies=30, min_retweets=100, count=10, bias=0):
        print(f'{query} min_replies:{min_replies} min_retweets:{min_retweets}')
        buz_tweet_list = self.api.search_tweets(q=f'{query} min_replies:{min_replies} min_retweets:{min_retweets}',
                                         lang='ja', count=count, tweet_mode="extended")
        a = self.analyst
        damaged_tweets = []
        not_damaged_tweets = []
        for buz_tweet in buz_tweet_list:
            limit = self.get_tweet_search_show_limit()
            if limit < 3:
                while True:
                    time.sleep(60 * 1)
                    limit = self.get_tweet_search_show_limit()
                    if limit > 3:
                        break

            reply_ambience, quoted_retweet_ambience = self.get_comment_ambience(original_tweet=buz_tweet)

            print('----------------------------')
            print(f'reply_ambience_score:{reply_ambience}')
            print(f'quoted_retweet_ambience_score:{quoted_retweet_ambience}')

            if reply_ambience < bias or quoted_retweet_ambience < bias:
                self.print_detailed_tweet_info(buz_tweet)
                damaged_tweets.append(buz_tweet)
            else:
                not_damaged_tweets.append(buz_tweet)

        return damaged_tweets, not_damaged_tweets

    def print_tweet_sentiment_score(self, tweet, pn_classifier=None):
        replys = self.get_reply(original_tweet=tweet, max_count=50)
        quoted_retweets = self.get_quoted_retweet(original_tweet=tweet, max_count=50)

        if pn_classifier == 'positive' or pn_classifier == 'negative':
            pos_replys, neg_replys = self.classifier_pos_neg_sentence(replys)
            pos_quoted_retweets, neg_quoted_retweets = self.classifier_pos_neg_sentence(quoted_retweets)
            if pn_classifier == 'positive':
                self.calculate_tweet_sentiment_score(pos_replys)
                self.calculate_tweet_sentiment_score(pos_quoted_retweets)
            if pn_classifier == 'negative':
                self.calculate_tweet_sentiment_score(neg_replys)
                self.calculate_tweet_sentiment_score(neg_quoted_retweets)
            return

        self.calculate_tweet_sentiment_score(replys)
        self.calculate_tweet_sentiment_score(quoted_retweets)

    def print_inside_calc_sentiment_score(self, tweet, pn_classifier=None):
        replys = self.get_reply(original_tweet=tweet, max_count=50)
        quoted_retweets = self.get_quoted_retweet(original_tweet=tweet, max_count=50)

        if pn_classifier == 'positive' or pn_classifier == 'negative':
            pos_replys, neg_replys = self.classifier_pos_neg_sentence(replys)
            pos_quoted_retweets, neg_quoted_retweets = self.classifier_pos_neg_sentence(quoted_retweets)
            if pn_classifier == 'positive':
                self.inside_calc_sentiment_score(pos_replys)
                self.inside_calc_sentiment_score(pos_quoted_retweets)
            if pn_classifier == 'negative':
                self.inside_calc_sentiment_score(neg_replys)
                self.inside_calc_sentiment_score(neg_quoted_retweets)
            return

        self.calculate_tweet_sentiment_score(replys)
        self.calculate_tweet_sentiment_score(quoted_retweets)

    def print_tweet_ambience(self, tweet):
        a = self.analyst
        reply_ambience, quoted_retweet_ambience = self.get_comment_ambience(original_tweet=tweet)

        print('----------------------------')
        print(f'reply_ambience_score:{reply_ambience}')
        print(f'quoted_retweet_ambience_score:{quoted_retweet_ambience}')

    def research(self, tweet):
        self.count_follower_retweets(tweet)

    def split_url(self, url):
        # urlからスクリーンネームとtweetのidを取得する
        split_url = url.split('/')
        unrelated_words = ['https:', '', 'twitter.com', 'status']
        related_words = []
        for word in split_url:
            if word in unrelated_words:
                continue
            related_words.append(word)
        related_words[0] = '@' + related_words[0]
        return related_words

    def print_tweet_info(self, tweet):
        print('----------------------------')
        print(f'user name:{tweet.user.name}')
        print(f'created_at:{tweet.created_at}')
        print(f'text:\n{tweet.full_text}')
        print('----------------------------')

    def print_detailed_tweet_info(self, tweet):
        print('----------------------------')
        print(f'user name:{tweet.user.name}')
        print(f'created_at:{tweet.created_at}')
        print(f'favorite:{tweet.favorite_count}, retweet_count:{tweet.retweet_count}')
        print(f'URL:https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}')
        print(f'text:\n{tweet.full_text}')
        print('----------------------------')

    def get_tweet_url(self, tweet):
        url = f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}'
        return url

    def count_follower_retweets(self, tweet):
        retweets = self.api.retweets(tweet.id, 10000)
        random.shuffle(retweets)

        count = 0
        follower_retweet_count = 0
        follower_favorite_count = 0
        for retweet in retweets:
            # 10回ループしたら終了
            if count >= 10:
                break

            # フォローチェック
            time.sleep(1)
            friendship = self.api.show_friendship(tweet.user.id, tweet.user.screen_name, retweet.user.id, retweet.user.screen_name)
            if friendship[1].following:
                follower_retweet_count += 1
            count += 1

        print(f'合計リツイート数:{len(retweets)}, フォロワーリツイート:{follower_retweet_count}/{count}')

    def show_rate_limit(self):
        limit = self.api.rate_limit_status()
        print("{}".format((json.dumps(limit, indent=4))))

    def get_friendship_show_limit(self):
        limit = self.api.rate_limit_status()
        return limit["resources"]["friendships"]["/friendships/show"]["remaining"]

    def get_tweet_search_show_limit(self):
        limit = self.api.rate_limit_status()
        return limit["resources"]["search"]["/search/tweets"]["remaining"]

    def sleep_api(self):
        limit = self.get_tweet_search_show_limit()
        if limit < 3:
            while True:
                time.sleep(60 * 1)
                limit = self.get_tweet_search_show_limit()
                if limit > 3:
                    break
        return

    def search_burning_tweet(self, query='', min_replies=30, min_retweets=100, count=10, bias=0):
        print(f'{query} min_replies:{min_replies} min_retweets:{min_retweets}')
        buz_tweet_list = self.api.search_tweets(q=f'{query} min_replies:{min_replies} min_retweets:{min_retweets}',
                                         lang='ja', count=count, tweet_mode="extended")
        emotion_analyst = MLAsk()
        burning_tweets = []
        not_burning_tweets = []
        for buz_tweet in buz_tweet_list:
            positive_comments = []
            neutral_comments = []
            negative_comments = []
            limit = self.get_tweet_search_show_limit()
            if limit < 3:
                while True:
                    time.sleep(60 * 1)
                    limit = self.get_tweet_search_show_limit()
                    if limit > 3:
                        break
            replys = self.get_reply(original_tweet=buz_tweet, max_count=50)
            quoted_retweets = self.get_quoted_retweet(original_tweet=buz_tweet, max_count=50)

            if len(replys) != 0:
                reply_comments = []
                for reply in replys:
                    reply_comments.append(reply.full_text)
                for comment in reply_comments:
                    result = emotion_analyst.analyze(comment)
                    print(result)
                    comment_emotion = result["orientation"]
                    if comment_emotion == 'POSITIVE':
                        positive_comments.add(comment)
                    if comment_emotion == 'NEUTRAL':
                        neutral_comments.add(comment)
                    if comment_emotion == 'NEGATIVE':
                        negative_comments.add(comment)

            if len(quoted_retweets) != 0:
                quoted_retweet_comments = []
                for quoted_retweet in quoted_retweets:
                    quoted_retweet_comments.append(quoted_retweet.full_text)
                for comment in quoted_retweet_comments:
                    result = emotion_analyst.analyze(comment)
                    comment_emotion = result["orientation"]
                    if comment_emotion == 'POSITIVE':
                        positive_comments.add(comment)
                    if comment_emotion == 'NEUTRAL':
                        neutral_comments.add(comment)
                    if comment_emotion == 'NEGATIVE':
                        negative_comments.add(comment)

            sum_comment = len(replys) + len(quoted_retweets)
            if float(negative_comments) > sum_comment / 3:
                burning_tweets.add(buz_tweet)
            else:
                not_burning_tweets.add(buz_tweet)

        return burning_tweets, not_burning_tweets

    def EgoSearch(self):

        personal_information = pd.read_csv("personal_information2.csv", encoding="UTF-8")
        personal_names = personal_information['氏名'].tolist()

        """
        personal_names = []
        for i in [2, 3, 4]:
            personal_information = pd.read_csv(f"personal_information{i}.csv", encoding="UTF-8")
            personal_information = personal_information['氏名'].tolist()
            personal_names = personal_names + personal_information
        """

        # 検索する名前の数を指定する
        # personal_names = personal_names[60:100]

        success_keyword = []

        for personal_name in personal_names:
            while True:
                try:
                    limit = self.get_tweet_search_show_limit()
                    break
                except:
                    print('制限回復中1')
                    time.sleep(60 * 1)
            if limit < 3:
                while True:
                    print('制限回復中2')
                    time.sleep(60 * 1)
                    try:
                        limit = self.get_tweet_search_show_limit()
                        break
                    except:
                        print('制限回復中1')
                        time.sleep(60 * 1)
                    if limit > 3:
                        break
            tweet_list = self.api.search_tweets(q=f'"{personal_name}"', count=100, tweet_mode="extended")
            if len(tweet_list) != 0:
                success_keyword.append(personal_name)

            print(f'"{personal_name}"に関するツイートの数:{len(tweet_list)}')

        print('一週間以内にツイートがあった人')
        for keyword in success_keyword:
            print(keyword)
        return

    def eaa(self):
        tweet_list = self.api.search_tweets(q='"岩本義弘"', count=100, tweet_mode="extended")
        for tweet in tweet_list:
            print('-----------')
            print(f'user_name:{tweet.user.name}')
            print(f'url:{self.get_tweet_url(tweet=tweet)}')
            print(f'text:{tweet.full_text}')
        return

    def get_comment_csv(self, url, file_name, max_count=100):
        tweet = self.get_tweet_from_url(url)
        reply_comment, quoted_retweet_comment = self.get_comment(tweet, max_count=max_count)
        reply_comment = self.sub_comments(reply_comment)
        quoted_retweet_comment = self.sub_comments(quoted_retweet_comment)
        comment = reply_comment + quoted_retweet_comment
        with open(f'コメント/{file_name}.csv', 'w', encoding="UTF-8") as f:
            writer = csv.writer(f, delimiter="\n")
            writer.writerow(comment)
        return

    def sub_comments(self, comments):
        strip_comments = []
        for comment in comments:
            strip_comment = re.sub('@.+ ', '', comment)
            strip_comment = re.sub('http.+', '', strip_comment)
            strip_comments.append(strip_comment)
        return strip_comments

    def concat_csv(self):
        csv_files = glob.glob('コメント/リベラル/*.csv')

        for file in csv_files:
            print(file)

        data_list = []

        for file in csv_files:
            data_list.append(pd.read_csv(file))

        df = pd.concat(data_list, axis=0, sort=True)
        df.to_csv("コメント/リベラル/統括/統括.csv", index=False)
        return