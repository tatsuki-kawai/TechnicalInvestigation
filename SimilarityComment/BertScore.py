from bert_score import score

def calc_bert_score(cands, refs):
    Precision, Recall, F1 = score(cands, refs, lang="ja", verbose=True)
    return F1.numpy().tolist() #F1のみ返す

if __name__ == "__main__":
    with open("test.txt", errors='ignore') as f:
        list = [line.strip() for line in f]

    result = []
    for index, item in enumerate(list):
        cands = []
        for item in list:
            cands.append(list[index]) #総当たり用配列

        F1 = calc_bert_score(cands, list)
        data = []
        for i, item in enumerate(F1):
            data.append([item, i])
        del data[index]
        data.sort(reverse=True)
        result.append(data)

        print(data)

    for i, item in enumerate(result):
        n = 0
        print(list[i])
        for score in item:
            print("   " + str(score[0]) + " : " + list[score[1]])