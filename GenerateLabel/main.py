# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from GenerateLabelCollectionDocument import GenerateLabelCollectionDocument
from GenerateLabelCollectionDocument import WordSurfacePhrase

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    collection = ["一番の被害者はたった一人残された子供だね。本当にお気の毒としか言えない。父親が母親を殺害した事に、どれだけショックを受けたことか、想像に難くない。まだ、10歳という年齢を考えると将来の事が心配だ。どちらかの祖父母が後見人となり、育てるのだろうが、心中察するに余りあるものがある。"]
    collection = ["一番の被害者はたった一人残された子供だね。本当にお気の毒としか言えない。父親が母親を殺害した事に、どれだけショックを受けたことか、想像に難くない。まだ、10歳という年齢を考えると将来の事が心配だ。どちらかの祖父母が後見人となり、育てるのだろうが、心中察するに余りあるものがある。",
                  "これまでの立派な経緯や努力、研究等、人生を帳消しにしてしまったね。何故？奥さんにそんなものを、、詳しくは分からないけど何か事情が有ったにせよ、命まで奪うなんて酷すぎる。御長男が気の毒だ。",
                  "そこまでの知識がありながらメタノールを選ぶだなんて。何より、殺さなくても別れれば済む話だったのでは。お子さんにとっては自慢のお父さんお母さんだっただろうに。心のケアが心配だ。",
                  "パッと見イケメンやし、研究者としてのキャリアも一流企業の社員としてのキャリアも積んでる。何が不満なんだって人生やな。",
                  "同じ会社なら何かしらの兆候を感じ取っていたりしないのか動機は勿論大事だが子どもの将来や相手自分の人生を壊してまで犯罪をやろうという傾向が怖いな最近論理性がない事件が多過ぎる",
                  "半年以上経ってからの逮捕。これは身内や知り合いからの捜査依頼などを受けての逮捕かしら？だとしたら、ひとりの父親である容疑者が子どもの成長を見守るために黙認するか、身内や知り合いがよほど耐えきれず警察へ依頼したか、でしょうか？"]
    fw = WordSurfacePhrase(collection=collection)
    #fw.wakati_collection()
    #fw.split_space_collection()
    # print(fw.collection)
    # fw.frequent_word()
    for phrase_list in fw.ngram_range_extract_phrase_rank_watf(start_n=2, end_n=3, threshold=False):
        print(phrase_list)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
