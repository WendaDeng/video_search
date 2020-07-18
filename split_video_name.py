import os

video_dir = '/home/xuezhuangzhuang/data/split_tacos'
result = []
for video_name in os.listdir(video_dir):
    if video_name.endswith('.avi'):
        data = video_name[:-4].split('_')
        result.append(data[0] + '_' + data[4] + ':' + data[1] + ',' + data[5] + ',' + data[2] + ',' + data[3])

with open('./tacos_result.txt', 'w') as f:
    for item in result:
        f.write(item + '\n')
