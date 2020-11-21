import os
import time
import heapq

import numpy as np
import torch

from .model import Net
from .dataloader_predict import video_dataloader, text_embedding
__all__ = ['predict']


def predictor(video_data, caption_embedding, top_k, model_params_root):
    video_modality_dim = {'visual': (2048, 2048), 'motion': (1024, 1024), 'instance': (2048, 2048)}
    net = Net(video_modality_dim, 500, audio_cluster=16, text_cluster=32)
    net.load_state_dict(torch.load(model_params_root))
    net.cuda()
    net.eval()
    video_ids = []
    scores = torch.zeros((len(video_data)))
    for idx, (data, vid) in enumerate(video_data):
        instance = data['instance'].cuda()
        video = data['video'].cuda()
        flow = data['flow'].cuda()
        ind = {}
        ind['instance'] = np.ones((len(video)))
        ind['visual'] = np.ones((len(video)))
        ind['motion'] = np.ones((len(video)))
        conf = net(caption_embedding.reshape(1, 30, 500).cuda(),{'instance': instance,
                                   'visual': video, 'motion': flow}, ind, True)
        scores[idx] = conf[0][0]
        video_ids.append(vid[0][0])
    scores = scores.data.cpu().numpy()
    # max_num_index_list = map(scores.index, heapq.nlargest(3, scores))
    max_num_index_list = heapq.nlargest(top_k, range(len(scores)), scores.take)
    idx = list(max_num_index_list)
    video_name_list = []
    for i in idx:
        video_name_list.append(video_ids[int(i)])
    scores_list = scores[idx].tolist()
    return video_name_list, scores_list


def predict(caption, top_k=10, visual_feat_path=None, flow_feat_path=None, 
            instances_features_path=None, word2vec_root=None, model_params_root=None):
    video_data = video_dataloader(visual_feat_path, batch_size=1, num_workers=2, 
                                  flow_features_path=flow_feat_path, instance_features_path=instances_features_path)
    caption_embedding = text_embedding(caption, word2vec_root=word2vec_root)
    video_name_list, scores_list = predictor(video_data, caption_embedding, top_k, model_params_root)
    return video_name_list, scores_list
