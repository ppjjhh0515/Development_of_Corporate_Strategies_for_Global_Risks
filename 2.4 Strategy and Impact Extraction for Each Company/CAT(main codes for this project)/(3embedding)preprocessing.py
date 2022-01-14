"""Creating fragments takes a long time so we treat it as a
pre-processing step."""
import logging
import json
import sys
sys.path.append('.')
from gensim.models import Word2Vec
from cat.fragments import create_noun_counts
from cat.utils import conll2text
from collections import Counter

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":

    paths = ["data/para.conllu"]
    create_noun_counts(paths,
                       "data/nouns.json")
    conll2text(paths, "data/all_txt.txt")
    print('conll2text finished.')
    corpus = [x.lower().strip().split()
              for x in open("data/all_txt.txt", encoding='utf-8')]
    print('loaded text finished')
    f = Word2Vec(corpus,
                 sg=0,
                 negative=5,
                 window=10,
                 vector_size=200,
                 min_count=2,
                 epochs=5,
                 workers=10)
    print('word2vec training finished')
    f.wv.save_word2vec_format("embeddings/my_para_word_vectors.vec")
    print('save embedding finished')
    d = json.load(open("data/nouns.json", encoding='utf-8'))
    nouns = Counter()
    for k, v in d.items():
        if k.lower() in f.wv:
            nouns[k.lower()] += v

    nouns, _ = zip(*sorted(nouns.items(),
                           key=lambda x: x[1],
                           reverse=True))

    json.dump(nouns, open("data/para_aspect_words.json", "w"))
    print("dump json finished")