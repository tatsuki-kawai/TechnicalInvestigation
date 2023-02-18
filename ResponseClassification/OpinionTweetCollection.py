import TweetSearcher
import TweetDB
import time

class OpinionTweetCollection:
    def __init__(self):
        self.keyword = {"経済", "労働", "最低賃金", "学歴", "格差", "フェミニズム", "表現の自由", "性犯罪", "表現規制", "萌え絵",
                        "政策", "貧困", "名誉棄損", "ジェンダー", "謝罪", "外国人", "移民", "夫婦別姓", "左翼", "右翼", "デマ",
                        "反ワクチン", "薬害", "誹謗中傷", "パヨク", "ネトウヨ", "反日"}
        self.searcher = TweetSearcher.TweetSearcher()

    def collect_opinion_tweet(self):
        # DAOインスタンスの生成
        tweetDB = TweetDB.TweetDatabasePsycopg2()

        opinions = []
        querys = []

        for word in self.keyword:
            query = word
            self.searcher.sleep_api()
            tweets = self.searcher.search_tweet_list(query=f"{query} min_replies:10", max_count=20)
            for tweet in tweets:
                while True:
                    self.searcher.print_detailed_tweet_info(tweet)
                    option = int(input('選択肢を選んでください。1.意見、2．意見ではない -----> '))

                    if option == 1:
                        opinions.append(tweet)
                        querys.append(word)
                    break
        return opinions, querys

    def collect_opinion_tweet_from_url(self):
        opinions = []
        while True:
            string = input("URLを入れてください(終了は”exit”) -----> ")
            if string == "exit":
                break
            tweet = self.searcher.get_tweet_from_url(url=string)
            if tweet is not None:
                opinions.append(tweet)
        print(len(opinions))
        return opinions

