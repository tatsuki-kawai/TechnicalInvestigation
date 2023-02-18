import TweetDB
import DataCollection
import ClassificationModel

# ガター内の緑色のボタンを押すとスクリプトを実行します。
if __name__ == '__main__':
    # dataCollection = DataCollection.TweetCollection()
    # dataCollection.get_tweet()

    url = TweetDB.TweetDatabasePsycopg2().get_comment_url(id=981)
    print(url)

    dataAnnotation = DataCollection.DataAnnotation()
    # dataAnnotation.get_data()
    # dataAnnotation.annotation(opinion_type=1)

    # ClassificationModel.practice()

    # text = "それは、日本に侵略したい連中の謀略の一つですから、\nマスコミはソイツらと\nグルです。 https://t.co/CZ6xt7NbRz"
    # text2 ="@NatsukiYasuda これは外国人に限った話ではないでしょう？容疑者の人権として論じるところが、外国人の人権の話になっていて、" \
    #        "論点をずらしているように思えます。"
    # text3 = "なんのための報じるのか。\n\n#d4p #安田菜津紀\n\n“報じる側にとっては、日々の仕事の中の「一瞬」かもしれないが、誤った形で名前を" \
    #         "晒された側にとって、その被害は長期間に渡りつきまとってくる。なぜ、なんのためにそれを報じるのか？それを報じることで誰かの人権を" \
    #         "無為に踏みにじってしまわないか？“ https://t.co/eVVj0ZxupI"
    # text4 = "日本に住む外国人の方々への酷い扱い\n胸が痛い。🥶\n＃在日外国人の人権保障を https://t.co/hMWPZ6FAu7"
    # text5 = "なんのための報じるのか。\n\n#d4p #安田菜津紀\n\n“報じる側にとっては、日々の仕事の中の「一瞬」かもしれないが、" \
    #         "誤った形で名前を晒された側にとって、その被害は長期間に渡りつきまとってくる。なぜ、なんのためにそれを報じるのか？" \
    #         "それを報じることで誰かの人権を無為に踏みにじってしまわないか？“ https://t.co/eVVj0ZxupI"
    # text6 = "本当です。私、某有名な大阪市内のコロナ病棟近所なんでただオミクロンの検体は時間かかるから後手後手みたいと、聞きました。オミクロンの怖さは" \
    #         "ワクチン接種に感染したら重症懸念の話が出ている。ワクチン未接種には逆に弱毒という話も出回り、まだわかりません感染疑念の病院はまだ公表なし"
    # text7 = "なんで？と思ってた。今更だけど"
    #
    # dataAnnotation.preprocessing.test_preprocessing(text4)