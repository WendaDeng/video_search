#!/usr/bin/env python
#encoding: utf-8
"""
@author: Huaqiao Han
@contact: huaqiao0629@gmail.com
@time: 2019/11/26 9:40
@file：vocab.py
@desc：
"""
# Create a vocabulary wrapper
from __future__ import print_function
import pickle
from collections import Counter
import json
import argparse
import os
import sys
sys.path.append('/home/hanhuaqiao/image/rt/project/Text_to_Video_Retrieval/dual_encoding/util')
import re
import collections
import numpy as np
import time
'''
本文件的目的是处理文本数据
    出去标点符号、出现次数低于5次的单词删除、输出单词数目
'''
def checkToSkip(filename, overwrite):
    if os.path.exists(filename):
        print ("%s exists." % filename),
        if overwrite:
            print ("overwrite")
            return 0
        else:
            print ("skip")
            return 1
    return 0

def makedirsforfile(filename):
    try:
        os.makedirs(os.path.split(filename)[0])
    except:
        pass

class Progbar(object):
    """Displays a progress bar.
       该函数实际上实现了进度条的显示，没有什么实际作用
    # Arguments
        target: Total number of steps expected, None if unknown.
        width: Progress bar width on screen.
        verbose: Verbosity mode, 0 (silent), 1 (verbose), 2 (semi-verbose)
        stateful_metrics: Iterable of string names of metrics that
            should *not* be averaged over time. Metrics in this list
            will be displayed as-is. All others will be averaged
            by the progbar before display.
        interval: Minimum visual progress update interval (in seconds).
    """

    def __init__(self, target, width=30, verbose=1, interval=0.05,
                 stateful_metrics=None):
        self.target = target
        self.width = width
        self.verbose = verbose
        self.interval = interval
        if stateful_metrics:
            self.stateful_metrics = set(stateful_metrics)
        else:
            self.stateful_metrics = set()
        #hasattr(object,name),object：对象  name:字符串，属性名  如果对象有该属性返回 True，否则返回 False。
        self._dynamic_display = ((hasattr(sys.stdout, 'isatty') and
                                  sys.stdout.isatty()) or
                                 'ipykernel' in sys.modules)
        self._total_width = 0
        self._seen_so_far = 0
        self._values = collections.OrderedDict()
        self._start = time.time()
        self._last_update = 0

    def update(self, current, values=None):
        """Updates the progress bar.

        # Arguments
            current: Index of current step.
            values: List of tuples:
                `(name, value_for_last_step)`.
                If `name` is in `stateful_metrics`,
                `value_for_last_step` will be displayed as-is.
                Else, an average of the metric over time will be displayed.
        """
        values = values or []
        for k, v in values:
            if k not in self.stateful_metrics:
                if k not in self._values:
                    self._values[k] = [v * (current - self._seen_so_far),
                                       current - self._seen_so_far]
                else:
                    self._values[k][0] += v * (current - self._seen_so_far)
                    self._values[k][1] += (current - self._seen_so_far)
            else:
                self._values[k] = v
        self._seen_so_far = current

        now = time.time()
        info = ' - %.0fs' % (now - self._start)
        if self.verbose == 1:
            if (now - self._last_update < self.interval and
                    self.target is not None and current < self.target):
                return

            prev_total_width = self._total_width
            if self._dynamic_display:
                sys.stdout.write('\b' * prev_total_width)
                sys.stdout.write('\r')
            else:
                sys.stdout.write('\n')

            if self.target is not None:
                numdigits = int(np.floor(np.log10(self.target))) + 1
                barstr = '%%%dd/%d [' % (numdigits, self.target)
                bar = barstr % current
                prog = float(current) / self.target
                prog_width = int(self.width * prog)
                if prog_width > 0:
                    bar += ('=' * (prog_width - 1))
                    if current < self.target:
                        bar += '>'
                    else:
                        bar += '='
                bar += ('.' * (self.width - prog_width))
                bar += ']'
            else:
                bar = '%7d/Unknown' % current

            self._total_width = len(bar)
            sys.stdout.write(bar)

            if current:
                time_per_unit = (now - self._start) / current
            else:
                time_per_unit = 0
            if self.target is not None and current < self.target:
                eta = time_per_unit * (self.target - current)
                if eta > 3600:
                    eta_format = '%d:%02d:%02d' % (eta // 3600, (eta % 3600) // 60, eta % 60)
                elif eta > 60:
                    eta_format = '%d:%02d' % (eta // 60, eta % 60)
                else:
                    eta_format = '%ds' % eta

                info = ' - ETA: %s' % eta_format
            else:
                if time_per_unit >= 1:
                    info += ' %.0fs/step' % time_per_unit
                elif time_per_unit >= 1e-3:
                    info += ' %.0fms/step' % (time_per_unit * 1e3)
                else:
                    info += ' %.0fus/step' % (time_per_unit * 1e6)

            for k in self._values:
                info += ' - %s:' % k
                if isinstance(self._values[k], list):
                    avg = np.mean(
                        self._values[k][0] / max(1, self._values[k][1]))
                    if abs(avg) > 1e-3:
                        info += ' %.4f' % avg
                    else:
                        info += ' %.4e' % avg
                else:
                    info += ' %s' % self._values[k]

            self._total_width += len(info)
            if prev_total_width > self._total_width:
                info += (' ' * (prev_total_width - self._total_width))

            if self.target is not None and current >= self.target:
                info += '\n'

            sys.stdout.write(info)
            sys.stdout.flush()

        elif self.verbose == 2:
            if self.target is None or current >= self.target:
                for k in self._values:
                    info += ' - %s:' % k
                    avg = np.mean(
                        self._values[k][0] / max(1, self._values[k][1]))
                    if avg > 1e-3:
                        info += ' %.4f' % avg
                    else:
                        info += ' %.4e' % avg
                info += '\n'

                sys.stdout.write(info)
                sys.stdout.flush()

        self._last_update = now

    def add(self, n, values=None):
        self.update(self._seen_so_far + n, values)

class Vocabulary(object):
    """Simple vocabulary wrapper."""

    def __init__(self, text_style='bow'):
        self.word2idx = {}
        self.idx2word = {}
        self.idx = 0
        self.text_style = text_style

    def add_word(self, word):
        if word not in self.word2idx:
            self.word2idx[word] = self.idx
            self.idx2word[self.idx] = word
            self.idx += 1
    #该类实现的__call__()函数，本质上是为self.text_style='rnn'实现的
    def __call__(self, word):
        if word not in self.word2idx and 'bow' not in self.text_style:
            return self.word2idx['<unk>']
        return self.word2idx[word]

    def __len__(self):
        return len(self.word2idx)




def clean_str(string):
    string = re.sub(r"[^A-Za-z0-9]", " ", string)
    return string.strip().lower().split()

def from_txt(txt):
    #该函数返回所有的caption，类型为list
    captions = []
    #print("txt::",txt)
    with open(txt, 'rb') as reader:
        for line in reader:
            #print(line)
            cap_id, caption = line.decode().split(' ',1)#分割caption id 和caption
            captions.append(caption.strip())

    return captions

def build_vocab(caption_file,text_style,threshold=4, ):
    # collection= 'msrvtt10ktrain'
    #text_style = 'bow'
    # rootpath= '/home/hanhuaqiao/VisualSearch'
    #threshold = 5
    """Build a simple vocabulary wrapper."""
    counter = Counter()
    #cap_file = os.path.join(rootpath, collection, 'TextData', '%s.caption.txt'%collection)
    #cap_file = '/home/hanhuaqiao/VisualSearch/msrvtt10ktrain/TextData/msrvtt10ktrain.caption.txt'
    captions = from_txt(caption_file)
    pbar = Progbar(len(captions))#实现进度条的显示

    for i, caption in enumerate(captions):
        tokens = clean_str(caption.lower())#把大写变小写
        counter.update(tokens)#更新counter,对每个单词出现的次数计数

        pbar.add(1)
        # if i % 1000 == 0:
        #     print("[%d/%d] tokenized the captions." % (i, len(captions)))
    #print("counter::",len(counter.items()))
    # Discard if the occurrence of the word is less than min_word_cnt.
    words = [word for word, cnt in counter.items() if cnt >= threshold]#只保存出现次数大于threshold的单词
    # Create a vocab wrapper and add some special tokens.
    print("length of words:",len(words))
    vocab = Vocabulary()
    # if 'rnn' in text_style:
    #     vocab.add_word('<pad>')
    #     vocab.add_word('<start>')
    #     vocab.add_word('<end>')
    #     vocab.add_word('<unk>')

    # Add words to the vocabulary.
    for i, word in enumerate(words):
        vocab.add_word(word)

    return vocab, counter


def main(caption_file,threshold,text_style):

    vocab_file = '/home/hanhuaqiao/VisualSearch/dataset/msrvtt_data/train_data/captions_data/vocabulary/bow/word_vocab_5.pkl'
    #counter_file = os.path.join(os.path.dirname(vocab_file), 'word_vocab_counter_%s.txt'%threshold)
    counter_file = '/home/hanhuaqiao/VisualSearch/dataset/msrvtt_data/train_data/captions_data/vocabulary/bow/word_vocab_counter_5.txt'
    vocab, word_counter = build_vocab(caption_file,text_style, threshold=threshold)
    with open(vocab_file, 'wb') as writer:
        pickle.dump(vocab, writer, pickle.HIGHEST_PROTOCOL)
    word_counter = [(word, cnt) for word, cnt in word_counter.items() if cnt >= threshold]
    word_counter.sort(key=lambda x: x[1], reverse=True)
    with open(counter_file, 'w') as writer:
        writer.write('\n'.join(map(lambda x: x[0]+' %d'%x[1], word_counter)))


if __name__ == '__main__':
    caption_file = '/home/hanhuaqiao/VisualSearch/dataset/msrvtt_data/train_data/captions_data/msrvtt10ktrain.caption.txt'
    rootpath= '/home/hanhuaqiao/VisualSearch'
    collection= 'msrvtt10ktrain'
    threshold = 5
    text_style = 'bow'
    overwrite = 0
    main(caption_file,threshold,text_style)

