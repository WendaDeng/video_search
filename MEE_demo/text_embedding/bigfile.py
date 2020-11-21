# -\*- coding: utf-8 -\*-
#!/usr/bin/env python
#encoding: utf-8
import os, array
import numpy as np

class BigFile:
    """
    BigFile类的默认输入为；shape.txt id_text.txt feature.bin 的所在文件夹
    read函数的输入为list,其内部存放的是要获取word2vec的单词
    """

    def __init__(self, datadir):
        #datadir输入的主目录，为/home/hanhuaqiao/VisualSearch/word2vec/flickr/vec500flickr30m
        #map(function, iterable, ...) function -- 函数  iterable -- 一个或多个序列 Python 2.x 返回列表。Python 3.x 返回迭代器。
        self.nr_of_words, self.ndims = map(int, open(os.path.join(datadir,'shape.txt')).readline().split())
        #上式返回的是 1743364 500，前一个参数为在wikipedia训练的单词数量，后一个参数为每个单词的维度
        #但是前一个参数的命名有问题
        id_file = os.path.join(datadir, "id_text.txt")
        self.names = open(id_file,encoding='utf8').read().strip().split(' ')#open(id_file,encoding='ISO-8859-1').read().strip().split()

        #上式获取了所有的单词，其数量为1743364，self.names的类型list
        assert(len(self.names) == self.nr_of_words)
        self.name2index = dict(zip(self.names, range(self.nr_of_words)))
        #上式获取每个单词和它们在词库中的id，并保存为字典格式
        self.binary_file = os.path.join(datadir, "feature.bin")
        #上式读取word 的enmbedding文件
        #print ("[%s] %dx%d instances loaded from %s" % (self.__class__.__name__, self.nr_of_words, self.ndims, datadir))


    def read(self, requested, isname=True):
        requested = set(requested)
        if isname:
            index_name_array = [(self.name2index[x], x) for x in requested if x in self.name2index]
        else:
            #这个判断的意义是什么？
            assert(min(requested)>=0)
            assert(max(requested)<len(self.names))
            index_name_array = [(x, self.names[x]) for x in requested]
        if len(index_name_array) == 0:
            return [], []
        index_name_array.sort(key=lambda x:x[0])
        sorted_index = [x[0] for x in index_name_array]
        nr_of_words_get = len(index_name_array)
        vecs = [None] * nr_of_words_get
        offset = np.float32(1).nbytes * self.ndims #获取每个单词500维向量的所占字节数
        
        res = array.array('f')#指定float类型序列，占4 bytes
        fr = open(self.binary_file, 'rb')
        fr.seek(index_name_array[0][0]  * offset)
        res.fromfile(fr, self.ndims)
        previous = index_name_array[0][0]
 
        for next in sorted_index[1:]:
            move = (next-1-previous) * offset
            #print next, move
            fr.seek(move, 1)
            #给 offset 定义一个参数，表示要从哪个位置开始偏移；0 代表从文件开头开始算起，1 代表从当前位置开始算起，2 代表从文件末尾算起。
            res.fromfile(fr, self.ndims)
            previous = next

        fr.close()
        words_name = []
        for x in index_name_array:
            words_name.append(x[1])

        words_embedding = []
        for i in range(nr_of_words_get):
            words_embedding.append(res[i * self.ndims:(i + 1) * self.ndims].tolist())
        #[x[1] for x in index_name_array], [ res[i*self.ndims:(i+1)*self.ndims].tolist() for i in range(nr_of_words_get) ]
        return words_name, words_embedding  # 返回单词 以及其embedding


    def read_one(self, name):
        renamed, vectors = self.read([name])
        return vectors[0]    

    # def shape(self):
    #     return [self.nr_of_words, self.ndims]

if __name__ == '__main__':
    bigfile = BigFile('/mnt/cephfs/hhq/paper_file/dataset/word2vec')

    print(bigfile.ndims)
    #imset = str.split('b z a a b c')
    renamed, vectors = bigfile.read(['q'])


    # for name,vec in zip(renamed, vectors):
    #     print (name, vec)
