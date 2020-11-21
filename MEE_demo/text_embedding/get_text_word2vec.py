import os
import pickle as pkl
import numpy as np
from text2vec import get_text_encoder
from collections import defaultdict
def text_word2vec_pos(caption_file,caption_embedding_root,word2vec_root):
    # video_caption = defaultdict(list)
    cap_ids = []
    #captions_embedding = []  # defaultdict(list)
    word2vec = get_text_encoder('word2vec')(word2vec_root)
    video_ids = []
    remaining_dict = defaultdict(list)
    noun_dict = defaultdict(list)
    remaining_embedding_path = open(os.path.join(caption_embedding_root,'remaining.pkl'),'wb')
    noun_embedding_path = open(os.path.join(caption_embedding_root,'noun.pkl'),'wb')
    with open(caption_file) as caption_file:
        lines = caption_file.readlines()
        for caption in lines:
            cap_idx, caption= caption.split(' ',1)
            video_idx = cap_idx.split('#')[0]
            remaining, noun = caption.strip().split('#')[2],caption.strip().split('#')[4]
            remaining_word_list = remaining.strip().split(' ')
            noun_word_list = noun.strip().split(' ')
            remaining_caption_embedding = np.zeros((len(remaining_word_list),500))
            noun_caption_embedding = np.zeros((len(noun_word_list),500))
            for idx in range(len(remaining_word_list)):
                embedding = word2vec.mapping(remaining_word_list[idx])
                if embedding is not None:
                    embedding = embedding.reshape(1,500)
                    remaining_caption_embedding[idx] = embedding
            for idx in range(len(noun_word_list)):
                embedding = word2vec.mapping(noun_word_list[idx])
                if embedding is not None:
                    embedding = embedding.reshape(1,500)
                    noun_caption_embedding[idx] = embedding
            remaining_dict[video_idx].append(remaining_caption_embedding)
            noun_dict[video_idx].append(noun_caption_embedding)    
    pkl.dump(remaining_dict,remaining_embedding_path)
    pkl.dump(noun_dict,noun_embedding_path)

    #return cap_idx, caption_embedding

def text_word2vec_all(caption_file,caption_embedding_root,word2vec_root):
    # video_caption = defaultdict(list)
    cap_ids = []
    #captions_embedding = []  # defaultdict(list)
    word2vec = get_text_encoder('word2vec')(word2vec_root)
    video_ids = []
    caption_dict = defaultdict(list)
    caption_embedding_path = open(os.path.join(caption_embedding_root,'caption_total_embedding.pkl'),'wb')
    with open(caption_file) as caption_file:
        lines = caption_file.readlines()
        for caption in lines:
            cap_idx, caption= caption.split(' ',1)
            video_idx = cap_idx.split('#')[0]
            caption_word_list = caption.strip().split(' ')
            caption_embedding = np.zeros((len(caption_word_list),500))
            for idx in range(len(caption_word_list)):
                embedding = word2vec.mapping(caption_word_list[idx])
                if embedding is not None:
                    embedding = embedding.reshape(1,500)
                    caption_embedding[idx] = embedding
            caption_dict[video_idx].append(caption_embedding)
    pkl.dump(caption_dict,caption_embedding_path)

    #return cap_idx, caption_embedding


if __name__ == '__main__':
    word2vec_root = '/mnt/cephfs/hhq/paper_file/dataset/word2vec'
    train_caption_file = '/mnt/cephfs/hhq/paper_file/dataset/FGAR_data/data/caption/noun_remaining_cap/train_caption_nuon_remain.txt'
    test_caption_file = '/mnt/cephfs/hhq/paper_file/dataset/FGAR_data/data/caption/noun_remaining_cap/test_caption_nuon_remain.txt'   
    caption_embedding_root = '/mnt/cephfs/hhq/paper_file/dataset/FGAR_data/caption_embedding/'
    caption_file = '/mnt/cephfs/hhq/paper_file/dataset/FGAR_data/data/caption/noun_remaining_cap/caption.txt'
    #text_word2vec_pos(caption_file,caption_embedding_root,word2vec_root=word2vec_root)
    caption_total = "/mnt/cephfs/hhq/paper_file/dataset/FGAR_data/msrvtt_caption/msrvtt10k_caption.txt"
    text_word2vec_all(caption_total,caption_embedding_root,word2vec_root)
   

