import numpy as np
import sys
import re
sys.path.append('./')

from .bigfile import BigFile
#from vocab import clean_str

INFO = __file__

def clean_str(string):
    string = re.sub(r"[^A-Za-z0-9]", " ", string)
    return string.strip().lower().split()

class Text2Vec(object):
    """ Text2Vec
        AveWord2Vec类的默认输入为；shape.txt id_text.txt feature.bin 的所在文件夹
        继承object是新式类，不继承为经典类
        当该类的子类重写了该类的方法，且被调用时，经典类会按照深度优先的方式去调用，新式类会按照广度优先的方式去调用
        且继承了object,比不继承多很多可调用对象
    """
    def __init__(self, datafile, ndims=0, L1_norm=0, L2_norm=0):

        self.datafile = datafile
        self.nidms = ndims
        self.L1_norm = L1_norm
        self.L2_norm = L2_norm

        assert (L1_norm + L2_norm) <= 1

    def preprocess(self, query, clear):
        if clear:
            words = clean_str(query)
        else:
            words = query.strip().split()
        return words

    def do_L1_norm(self, vec):
        L1_norm = np.linalg.norm(vec, 1)
        return 1.0 * np.array(vec) / L1_norm

    def do_L2_norm(self, vec):
        L2_norm = np.linalg.norm(vec, 2)
        return 1.0 * np.array(vec) / L2_norm

    def embedding(self, query):
        vec = self.mapping(query)
        if vec is not None:
            vec = np.array(vec)
        return vec

# Vocab
class Bow2Vec(Text2Vec):

    def __init__(self, vocab, ndims=0, L1_norm=0, L2_norm=0):
        super(Bow2Vec, self).__init__(vocab, ndims, L1_norm, L2_norm)

        self.vocab = vocab
        if ndims != 0:
            assert(len(self.vocab) == ndims) , \
                "feature dimension not match %d != %d" % (len(self.vocab), self.ndims)
        else:
            self.ndims = len(self.vocab)

    def mapping(self, query, clear=True):
        words = self.preprocess(query, clear)

        vec = [0.0]*self.ndims

        for word in words:
            if word in self.vocab.word2idx:
                vec[self.vocab(word)] += 1

        if sum(vec) > 0:

            if self.L1_norm:
                return self.do_L1_norm(vec)
            if self.L2_norm:
                return self.do_L2_norm(vec)

            return np.array(vec)

        else:
            return None



class AveWord2Vec(Text2Vec):
    """
    AveWord2Vec类的默认输入为；shape.txt id_text.txt feature.bin 的所在文件夹
    """
    def __init__(self, datafile, ndims=0, L1_norm=0, L2_norm=0):
        super(AveWord2Vec, self).__init__(datafile, ndims, L1_norm, L2_norm)

        self.word2vec = BigFile(datafile)
        if ndims != 0:
            assert(self.word2vec.ndims == ndims) , \
                "feature dimension not match %d != %d" % (self.word2vec.ndims, self.ndims)
        else:
            self.ndims = self.word2vec.ndims

    def mapping(self, query, clear=True):
        words = self.preprocess(query, clear)
        #上式返回小写变大写后的word,其返回类型为list
        renamed, vectors = self.word2vec.read(words)

        #说明有的单词数少于设定的阈值
        if len(renamed) != len(words):
            renamed2vec = dict(zip(renamed, vectors))
            vectors = []
            for word in words:
                if word in renamed2vec:
                    vectors.append(renamed2vec[word])


        if len(vectors) > 0:
            vec = np.array(vectors).mean(axis=0)

            if self.L1_norm:
                return self.do_L1_norm(vec)
            if self.L2_norm:
                return self.do_L2_norm(vec)

            return vec
        else:
            return None



NAME_TO_ENCODER = {'word2vec': AveWord2Vec, 'bow': Bow2Vec}


def get_text_encoder(name):
    assert name in NAME_TO_ENCODER
    return NAME_TO_ENCODER[name]
if __name__ == '__main__':
    t2v = AveWord2Vec('/home/hanhuaqiao/VisualSearch/dataset/word2vec')
    a = t2v.mapping('A people like you for me 1 93')
    print(a.shape)
    print(type(a))
