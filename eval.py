# %%
from rouge_chinese import Rouge
import jieba # Or other word cutting library
rouge = Rouge()
# %%
with open("answers.txt", 'r') as f:
    ls = f.read()
    std_ans = ls.split("\n\n\n\n")[:-1]
with open("gemma_answer.txt", 'r') as f:
    ls = f.read()
    gem_ans = ls.split("\n\n\n\n")[:-1]

# %%
s = []
for i in range(len(std_ans)):
    hyp = gem_ans[i]
    hyp = ' '.join(jieba.cut(hyp))
    ref = std_ans[i]
    ref = ' '.join(jieba.cut(ref))
    scores = rouge.get_scores(hyp, ref)
    s.append(scores[0])
# %%
fs_1 = [x["rouge-1"]["f"] for x in s]
aver1 = sum(fs_1)/len(fs_1)
print(aver1)
# %%
fs_2 = [x["rouge-2"]["f"] for x in s]
aver2 = sum(fs_2)/len(fs_2)
print(aver2)
# %%
fs_l = [x["rouge-l"]["f"] for x in s]
averl = sum(fs_l)/len(fs_l)
print(averl)
# %%
