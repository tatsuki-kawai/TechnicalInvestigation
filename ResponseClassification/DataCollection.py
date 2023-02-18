import re

import tweepy.errors

import OpinionTweetCollection
import TweetDB
import TweetSearcher
import psycopg2
import Object
import Preprocessing


class TweetCollection:
    def __init__(self):
        # self.opinionCollector = OpinionTweetCollection.OpinionTweetCollection()
        self.tweetDB = TweetDB.TweetDatabasePsycopg2()
        self.searcher = TweetSearcher.TweetSearcher()
        self.keyword1 = {"経済", "労働", "最低賃金", "学歴", "格差", "フェミニズム", "表現の自由", "性犯罪", "表現規制", "萌え絵",
                        "政策", "貧困", "名誉棄損", "ジェンダー", "外国人", "移民", "夫婦別姓", "左翼", "右翼", "デマ",
                        "反ワクチン", "薬害", "誹謗中傷", "パヨク", "ネトウヨ", "反日", "いじめ", "謝 "
                                                                           ""
                                                                           "罪"}

        self.keyword2 = {"#オミクロン接触者の受験不可の撤回を求めます"}

    def get_tweet(self):
        for word in self.keyword1:
            opinion_tweets = []
            querys = []
            query = word
            self.searcher.sleep_api()
            tweets = self.searcher.search_tweet_list(query=f"{query} min_replies:10", max_count=20)

            exist_opinion_list = self.tweetDB.get_all_opinion_tweet()
            exist_opinion_id_list = [exist_opinion[1] for exist_opinion in exist_opinion_list]
            exist_opinion_id_list = set(exist_opinion_id_list)

            exist_not_opinion_list = self.tweetDB.get_all_not_opinion_tweet()
            exist_not_opinion_id_list = [exist_not_opinion[1] for exist_not_opinion in exist_not_opinion_list]
            exist_not_opinion_id_list = set(exist_not_opinion_id_list)

            for tweet in tweets:
                if tweet.id in exist_opinion_id_list or tweet.id in exist_not_opinion_id_list:
                    continue

                while True:
                    self.searcher.print_detailed_tweet_info(tweet)
                    try:
                        option = int(input('選択肢を選んでください。1.意見、2．意見ではない -----> '))
                    except ValueError:
                        continue

                    if option == 1:
                        opinion_tweets.append(tweet)
                        querys.append(word)
                        break
                    if option == 2:
                        self.tweetDB.insert_not_opinion_tweet(tweet_id=tweet.id, user_id=tweet.user.id,
                                                              created_at=tweet.created_at, search_query=query,
                                                              text=tweet.full_text)
                        break

            # opinion_tweet_list, querys = self.opinionCollector.collect_opinion_tweet()
            for tweet_query_pair in zip(opinion_tweets, querys):
                opinion_tweet = tweet_query_pair[0]
                search_query = tweet_query_pair[1]
                if "https://t.co" in opinion_tweet.full_text or re.compile("@.+ ").search(opinion_tweet.full_text):
                    opinion_type = 1
                else:
                    opinion_type = 0
                if self.tweetDB.get_opinion_id(opinion_tweet.id) is None:
                    self.tweetDB.insert_opinion_tweet(opinion_tweet.id, opinion_tweet.user.id, opinion_tweet.created_at,
                                                      opinion_type, search_query, opinion_tweet.full_text)
                    self.searcher.sleep_api()
                    replys, quoted_retweets = self.searcher.get_comment_tweet(original_tweet=opinion_tweet,
                                                                              max_count=100)
                    for reply in replys:
                        try:
                            self.tweetDB.insert_comment_tweet(reply.id, self.tweetDB.get_opinion_id(opinion_tweet.id),
                                                              reply.user.id, "リプライ", reply.created_at, reply.full_text)
                        except psycopg2.Error:
                            continue

                    for quoted_retweet in quoted_retweets:
                        if "RT " in quoted_retweet.full_text:
                            continue
                        try:
                            self.tweetDB.insert_comment_tweet(quoted_retweet.id,
                                                              self.tweetDB.get_opinion_id(opinion_tweet.id),
                                                              quoted_retweet.user.id, "引用リツイート",
                                                              quoted_retweet.created_at, quoted_retweet.full_text)
                        except psycopg2.Error:
                            continue

class DataAnnotation:
    def __init__(self):
        self.tweetDB = TweetDB.TweetDatabasePsycopg2()
        self.searcher = TweetSearcher.TweetSearcher()
        self.preprocessing = Preprocessing.Preprocessing()

    def get_data(self):
        lines = self.tweetDB.join_opinion_comment()
        exist_lines = self.tweetDB.get_all_data()
        exist_opinion_id_list = [exist_line[1] for exist_line in exist_lines]
        exist_opinion_id_list = set(exist_opinion_id_list)

        t = 0
        for line in lines:
            if line[0] in exist_opinion_id_list:
                continue

            t += 1
            print(t)
            comment_text = line[5]
            # テキストの前処理
            comment_text = self.preprocessing.tweet_preprocessing(comment_text)
            comment_text = self.preprocessing.delete_emoji(comment_text)
            sents = self.preprocessing.trans_newline(comment_text)
            # sents = list(self.preprocessing.segment_splitter(text))

            # データの格納
            for i, sent in zip(range(1, len(sents)+1), sents):
                print(f"i:{i}, sent:{sent}")
                data = Object.Data(None, line[0], line[1], line[2], line[3], i, line[4], sent, None)
                if self.tweetDB.get_data_from_comment_tweet_id(line[3], i) is None:
                    self.tweetDB.insert_data(data)

    def annotation(self, annotation_type="without", opinion_type=0):
        # アノテーション方法の選択
        if annotation_type == "without":
            lines = self.tweetDB.get_data_without_label(opinion_type)

        # Dataオブジェクトの作成
        datalist = []
        for line in lines:
            data = Object.Data(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8])
            datalist.append(data)

        # アノテーション開始
        opinion_id_list = [data.opinion_id for data in datalist]
        opinion_id_list = set(opinion_id_list)
        for opinion_id in opinion_id_list:
            line = self.tweetDB.get_opinion_tweet(opinion_id)
            opinion = Object.Opinion(line[1], line[2], line[3], line[4], line[5], line[6])
            try:
                opinion_user = self.searcher.get_user_from_id(opinion.user_id)
                url = self.searcher.get_url(opinion_user.screen_name, opinion.tweet_id)
            except AttributeError:
                url = "ユーザが存在しません"
            except tweepy.errors.Forbidden:
                url = "ユーザが存在しません"

            comment_sentence_list = [data for data in datalist if data.opinion_id == opinion_id]
            comment_id_list = [comment_sentence.comment_id for comment_sentence in comment_sentence_list]
            comment_id_list = set(comment_id_list)
            comment_list = []
            for comment_id in comment_id_list:
                comment = [comment_sentence for comment_sentence in comment_sentence_list if
                           comment_sentence.comment_id == comment_id]
                comment_list.append(comment)
            while True:
                # 意見ツイートの表示の情報
                print("意見")
                print(f"{url}")
                print(f"text:\n{opinion.text}")

                # コメントの一覧の表示
                comment_number = 0
                for comment in comment_list:
                    comment_number += 1
                    print('----------------------------')
                    print(f"No.{comment_number}")
                    for sent in comment:
                        print(sent.comment_sentence)

                try:
                    print("\n")
                    option = int(input('アノテーションするコメントの番号を入力してください。0はスキップ -----> '))
                except ValueError:
                    continue

                if option == 0:
                    print("skip")
                    break

                # 選択したコメントのアノテーション
                option -= 1
                annotation_comment_sentence_list = comment_list[option]
                line = self.tweetDB.get_comment(annotation_comment_sentence_list[0].comment_id)
                annotation_comment = Object.Comment(line[1], line[2], line[3], line[4], line[5], line[6])
                comment_user = self.searcher.get_user_from_id(annotation_comment.user_id)

                print('----------------------------')
                print(f'opinion:\n{sent.opinion_text}')
                print('----------------------------')
                # print('----------------------------')
                print(f"comment:")
                print(f'URL:https://twitter.com/{comment_user.screen_name}/status/'
                      f'{annotation_comment.tweet_id}')
                [print(f"{i}:{sent.comment_sentence}") for i, sent in zip(
                    range(1, len(annotation_comment_sentence_list)+1), annotation_comment_sentence_list)]
                print('----------------------------')
                for i, sent in zip(
                        range(1, len(annotation_comment_sentence_list) + 1), annotation_comment_sentence_list):
                    while True:
                        try:
                            print(f"{i}:{sent.comment_sentence}")
                            option = int(input('選択肢を選んでください。1.賛成、2.否定、3.自説の提示, 4.ツイート行為の否定, 5.人格否定, 6.無関係, 7.未分類  -----> '))
                        except ValueError:
                            continue

                        option -= 1
                        if 0 <= option <= 6:
                            self.tweetDB.update_data(sent.id, option)
                            break