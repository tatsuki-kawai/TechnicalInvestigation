class Opinion:
    def __init__(self, tweet_id, user_id, created_at, opinion_type, search_query, text):
        self.tweet_id = tweet_id
        self.user_id = user_id
        self.created_at = created_at
        self.opinion_type = opinion_type
        self.search_query = search_query
        self.text = text

class Comment:
    def __init__(self, tweet_id, opinion_tweet_id, user_id, comment_type, created_at, text):
        self.tweet_id = tweet_id
        self.opinion_tweet_id = opinion_tweet_id
        self.user_id = user_id
        self.comment_type = comment_type
        self.created_at = created_at
        self.text = text

class Data:
    def __init__(self, id, opinion_id, comment_id, opinion_tweet_id, comment_tweet_id, number, opinion_text,
                 comment_sentence, label):
        self.id = id
        self.opinion_id = opinion_id
        self.comment_id = comment_id
        self.opinion_tweet_id = opinion_tweet_id
        self.comment_tweet_id = comment_tweet_id
        self.number = number
        self.opinion_text = opinion_text
        self.comment_sentence = comment_sentence
        self.label = label

