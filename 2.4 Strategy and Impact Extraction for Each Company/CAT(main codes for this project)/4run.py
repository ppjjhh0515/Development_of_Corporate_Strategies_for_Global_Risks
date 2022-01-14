import sys
sys.path.append('.')
from collections import defaultdict
from reach import Reach
from cat.simple import get_scores, rbf_attention
import json
import numpy as np

GAMMA = .03
N_ASPECT_WORDS = 20
N_TOPICS = 2
THRESH_HOLD = 0.3

if __name__ == "__main__":

    scores = defaultdict(dict)
    r = Reach.load("embeddings/my_word_vectors_sentence_level.vec",
                   unk_word="<UNK>")
    print('loaded word embedding')

    aspects = [[x]
               for x in json.load(open("data/aspect_words_sentence_level.json"))]
    aspects = aspects[:N_ASPECT_WORDS]

    with open('./10K/sentence.txt', 'r', encoding='utf-8') as f:
        instances = f.readlines()

    print('loaded instances to be predicted')

    instances = [x.split() for x in instances]
    label_set = ['financial flexibility','exit our joint venture investment','stop paying dividends',
    'maintained cash','additional funding','additional capital','preserve flexibility liquidity',

    'reduce costs','reduce expenses','decrease spending',

    'exited underperforming','focus core service','support services prolonged','deferred arrangements',
    'provide aftermarket service',
    'improve profitability','increasing discount rates','advertising cancellations','digital transformation',
    'experienced increase sales','reduced profitability','reduce operations','adjusting business plan',
    
    'remote working','avoid gatherings','impose travel restrictions','store closures',

    'capture new customers','demand variability customers',

    'reduce staffing','hiring reducing','retain key employees','damage employee relations',

    'sell composites','precautionary measure','reduce production', 'stoppage','prolonged work stoppage',
    'temporarily suspend','closure airframe maintenance','lower productivity','reduce inventory levels',
    
    'obtain materials','obtain supplies','find alternate sources','seek alternative suppliers',
    
    'increase evaluate sensitivity','assessing impact','relief and stimulus',
    'negatively impacts demand','economic and market uncertainty',
    'adversely affect business','impacted stock price','tax deferral',
    'sell shares','extend credit','disruptions supply','obtain clinical supplies']

    s = get_scores(instances,
                   aspects,
                   r,
                   label_set,
                   gamma=GAMMA,
                   remove_oov=False,
                   attention_func=rbf_attention)

    
    pred = np.argpartition(s, -N_TOPICS, axis=1)[:, -N_TOPICS:]
    probability = s[np.argpartition(s, -N_TOPICS, axis=1)[:, -N_TOPICS:]]
    print('prediction: ')
    print(pred)

    with open('data/prediction_Sentence(3).txt', 'w', encoding='utf-8') as f:
        for idx, x in enumerate(pred):
            inst = ' '.join(instances[idx])
            target_labels = []
            
            for idx, label_index in enumerate(x):
                if probability[idx][label_index] > THRESH_HOLD:
                    target_labels.append(label_set[label_index])
            target_labels = '\t'.join(target_labels)

            print(inst + target_labels + '\n', file=f)
