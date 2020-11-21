from MEE_demo.predict import predict

top_k = 10

flow_feat_path = './MEE_demo/data/msrvtt_flow_features_mee_mean.pkl'

word2vec_root = './MEE_demo/data/word2vec/'

instances_features_path = './MEE_demo/data/instances_bottom_up_features.pkl'

visual_feat_path = './MEE_demo/data/resnet152_features_pkl/msrvtt_resnet152_features_mee_f4.pkl'

model_params_root = './MEE_demo/model_params/params_f4_150.pkl'

caption = "cat and dog"

video_name_list, scores_list = predict(caption, top_k, visual_feat_path, flow_feat_path, instances_features_path, word2vec_root, model_params_root)

print(video_name_list, scores_list)
