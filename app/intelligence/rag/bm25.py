import math
from collections import Counter


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = docs
        self.k1 = k1
        self.b = b
        self.avgdl = sum(len(d) for d in docs) / len(docs)
        self.df = {}
        self.idf = {}
        self._build()

    def _build(self):
        N = len(self.docs)
        for doc in self.docs:
            for word in set(doc):
                self.df[word] = self.df.get(word, 0) + 1
        for word, freq in self.df.items():
            self.idf[word] = math.log(1 + (N - freq + 0.5) / (freq + 0.5))

    def score(self, query, doc):
        score = 0.0
        freqs = Counter(doc)
        for word in query:
            if word not in freqs:
                continue
            numerator = freqs[word] * (self.k1 + 1)
            denominator = freqs[word] + self.k1 * (
                1 - self.b + self.b * len(doc) / self.avgdl
            )
            score += self.idf.get(word, 0) * numerator / denominator
        return score
