#!/usr/bin/env python
#encoding: utf-8
"""
@author: Huaqiao Han
@contact: huaqiao0629@gmail.com
@time: 2019/11/29 15:43
@file：text_load_test.py
@desc：
"""
import os
import torch
import pickle
from text2vec import get_text_encoder
from vocab import clean_str
from vocab import Vocabulary
def get_text_data_loaders(caption,bow2vec):
    """
    Return caption(query) embedding
    :return:
    """
    cap_bow = bow2vec.mapping(caption)
    if cap_bow is None:
        cap_bow = torch.zeros(bow2vec.ndims)
    else:
        cap_bow = torch.Tensor(cap_bow)
    cap_bows = torch.zeros(1, 7807)
    cap_bows[0] = cap_bow
    return  cap_bow#返回单词的one-hot编码

if __name__ == '__main__':
    bow_vocab_file = '/home/hanhuaqiao/VisualSearch/dataset/msrvtt_data/train_data/captions_data/vocabulary/bow/word_vocab_5.pkl'
    bow_vocab = pickle.load(open(bow_vocab_file, 'rb'))
    bow2vec = get_text_encoder('bow')(bow_vocab)
    caption = 'a people like you'
    a = get_text_data_loaders(caption,bow2vec)
    print("**********************word2vec**********************")
    datafile = '/home/hanhuaqiao/VisualSearch/dataset/word2vec'
    word2vec = get_text_encoder('word2vec')(datafile)
    b = word2vec.mapping(caption)
    print(b)
    print(b.shape)
    print(type(b))