import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
import math
import random
import pickle
import pickle as pkl
MAX_FRAMES = 64
MAX_INSTANCES = 10
from .text_embedding.text2vec import get_text_encoder
class PredictDataset(Dataset):

    def __init__(self, visual_features,instances_features=None, flow_features=None, audio_features=None,max_words=30):
               
        self.max_words = max_words        
        visual_pickle = open(visual_features,'rb')
        self.visual_features = pickle.load(visual_pickle, encoding='iso-8859-1')

        self.length = len(self.visual_features)
        self.video_ids = []
        self.flow_features = None
        self.audio_features = None
        self.instances_features = None
        for idx in self.visual_features.keys():
            self.video_ids.append(idx)
        if flow_features:
            flow_pickle = open(flow_features,'rb')
            self.flow_features = pickle.load(flow_pickle, encoding='iso-8859-1')
        if audio_features:
            audio_pickle = open(audio_features,'rb')
            self.audio_features = pickle.load(audio_pickle, encoding='iso-8859-1')
        if instances_features:
            instance_pickle = open(instances_features,'rb')
            self.instances_features = pickle.load(instance_pickle, encoding='iso-8859-1')

    def __getitem__(self,index):
        video_ids = []
        vid = self.video_ids[index]
        video_ids.append(vid)
        video = self.visual_features[vid]
        flow = None
        audio = None
        instance = None
        if self.flow_features:
            flow = self.flow_features[vid][0]
        if self.audio_features:
            audio = self.audio_features[vid]
        if self.instances_features:
            instance = self.instances_features[vid]
        return {'video': video,
                'flow': flow,
                'instance': instance,
                'audio': audio
                } , video_ids 

    def __len__(self):
        
        return 1000# self.length

    def collate_data(self, video_data):
        data, video_ids = zip(*video_data)
        video_tensor = np.zeros((len(data),MAX_FRAMES,2048))
        flow_tensor = None 
        instance_tensor = None 
        audio_tensor = None 

        for i in range(len(data)):
            frames_length = len(data[i]['video'])
            video_tensor[i][0:min(frames_length,MAX_FRAMES)] = data[i]['video'][0:min(frames_length,MAX_FRAMES)]
            if data[0]['flow'] is not None:
                if flow_tensor is None:
                    flow_tensor = np.zeros((len(data), 1024))
              
                flow_tensor[i] = data[i]['flow']
            if data[0]['instance'] is not None:
                if instance_tensor is None:
                    instance_tensor = np.zeros((len(data),10, 2048))
               
                instance_tensor[i] = data[i]['instance'][3][0:10]
            if data[0]['audio'] is not None:
                if audio_tensor is None:
                    audio_tensor = np.zeros((len(data), self.max_words,128)) 
                la = len(data[i]['audio'])
                audio_tensor[i,:min(la,self.max_words), :] = data[i]['audio'][:min(self.max_words,la)]
        if flow_tensor is not None:
            flow_tensor = torch.from_numpy(flow_tensor).float()
        if instance_tensor is not None:
            instance_tensor = torch.from_numpy(instance_tensor).float()
           
        if audio_tensor is not None:
            audio_tensor = torch.from_numpy(audio_tensor).float()
        return {'video': torch.from_numpy(video_tensor).float(),
                'flow': flow_tensor,
                'instance': instance_tensor,
                'audio': audio_tensor}, video_ids

def video_dataloader(visual_feat_path, batch_size=1, shuffle=False, num_workers=1, flow_features_path=None, instance_features_path=None,
                      audio_features_path=None, max_words=30):
    dataset = PredictDataset(visual_feat_path, instance_features_path, flow_features_path, max_words=max_words)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, collate_fn=dataset.collate_data)
    return dataloader

def text_embedding(caption,max_words=30, word2vec_root='./data/word2vec'):
    word2vec = get_text_encoder('word2vec')(word2vec_root)
    caption_word_list = caption.strip().split(' ')
    caption_embedding = np.zeros((max_words,500))
    for idx in range(min(len(caption_word_list),max_words)):
        embedding = word2vec.mapping(caption_word_list[idx])
        if embedding is not None:
            embedding = embedding.reshape(1,500)
            caption_embedding[idx] = embedding
    caption_embedding = torch.from_numpy(caption_embedding).float()
    return caption_embedding


