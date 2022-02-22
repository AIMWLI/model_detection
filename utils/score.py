import numpy as np


class Constants(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Constants, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.HistLen = 500
        self.Weight = np.array([np.exp(i / (self.HistLen // 5)) for i in range(self.HistLen)])
        self.SumWeight = [np.sum(self.Weight[i:]) for i in range(self.HistLen)]


class HistoryScore(object):
    def __init__(self, seqdata, lastdata=None, seqorder='big'):
        """
        :param seqdata: [t0, t1, t2, ..., tn] n is the latest data.
        :param lastdata: None if the last data is in seqdata
        :param seqorder: big or True: t0->t1->t2->...->tn
                                    small or False: tn->...->t2->t1->t0
        """
        if seqorder.lower() not in ['big', True]:
            seqdata = seqdata[::-1]
        if lastdata is not None: seqdata.append(lastdata)
        self.seqdata = np.array([int(i) for i in seqdata[-Constants().HistLen:]])

    @property
    def score(self):
        if len(self.seqdata) == 0:
            return 0.8 * 100
        return 100 * np.matmul(Constants().Weight[-len(self.seqdata):], self.seqdata) / Constants().SumWeight[-len(self.seqdata)]


if __name__ == '__main__':
    from itertools import product

    seqlen = 5
    for seq in product(*[range(2)] * seqlen):
        print(seq, HistoryScore(seqdata=seq).score)
    print(HistoryScore(seqdata=[0, 1, 1]).score)