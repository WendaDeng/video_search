from __future__ import print_function

from collections import defaultdict

from flask import Flask, render_template, make_response
from flask import redirect, request, jsonify, url_for

import io
import os
import uuid
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

app = Flask(__name__)
app.secret_key = 's3cr3t'
app.debug = True
app._static_folder = os.path.abspath("templates/static/")

result_num = 20

# 生成 caption_content: caption_id 的字典
caption_dict = {}
with open('video_caption.txt') as f:
    lines = f.readlines()
for line in lines:
    data = line.strip().split(':')
    caption_dict[data[-1]] = data[0]

# 生成 caption_id: (video_id, video_score) 的字典
result_dict = {}
with open('caption_result.txt') as f:
    lines = f.readlines()
for line in lines:
    data = line.strip().split('---')
    result_dict[data[0]] = ':'.join(data[1:])

# 生成 tacos_query: query_id 字典
tacos_query_dict = {}
with open('tacos_query.txt') as f:
    lines = f.readlines()
for idx, line in enumerate(lines):
    tacos_query_dict[line.strip().lower()[:-1]] = str(idx)

# 生成 tacos_video: query_result 字典
tacos_result_dict = defaultdict(list)
with open('tacos_result.txt') as f:
    lines = f.readlines()
for line in lines:
    data = line.strip().split(':')
    tacos_result_dict[data[0]].append(data[1])


@app.route('/', methods=['GET'])
def index():
    return render_template('layouts/index.html', title='Multimedia Search Engine')


@app.route('/video_search', methods=['GET'])
def video_search():
    return render_template('layouts/video_search.html', title='Video Search')


@app.route('/video_localize', methods=['GET'])
def video_localize():
    return render_template('layouts/video_localize.html', title='Video Localize')


@app.route('/search', methods=['POST'])
def search():
    search_data = request.form['search_data'][1:-1]     # 去除多余的双引号 ""
    # 检查查询语句是否对应已有视频及查询结果
    caption_id = caption_dict[search_data] if search_data in caption_dict else None
    # 如果存在对应的查询结果，获取事先保存的结果
    result = result_dict[caption_id].split(':') if caption_id else None

    scores, video_names = [], []
    if result:
        video_names = result[0].split(',')[:result_num]
        scores = result[1].split(',')[:result_num]

    idxs = list(range(1, result_num + 1))
    params = {'video_names': video_names, 'scores': scores, 'idxs': idxs}
    return jsonify(params)


@app.route('/localize', methods=['POST'])
def localize():
    print('lllll')
    localize_str = request.form['localize_str'][1:-1]
    upload_video = request.form['upload_video']
    query_id = tacos_query_dict[localize_str.lower()] if localize_str.lower() in tacos_query_dict else None
    query_result = tacos_result_dict[upload_video + '_' + query_id] if query_id else None

    rank, scores, video_names = [], [], []
    for result in query_result:
        # result: score_rank_start-time_end-time
        data = result.split(',')
        rank.append(int(data[1]))
        # origin-video-name_score_start-time_end-time_query-id_rank
        video_names.append(upload_video + '_' + data[0] + '_' + data[2] + '_' + data[3] +
                           '_' + query_id + '_' + data[1])
        scores.append(data[0])
    # rank.sort()

    params = {'video_names': video_names, 'scores': scores, 'idxs': rank}
    return jsonify(params)


# 原有项目方法，展示结果
@app.route('/results/<uuid>', methods=['GET'])
def results(uuid):
    title = 'Result'
    data = get_file_content(uuid)
    return render_template('layouts/results.html',
                           title=title,
                           data=data)


# 原有项目方法，获取canvas数据
@app.route('/postmethod', methods=['POST'])
def post_javascript_data():
    js_data = request.form['canvas_data']
    unique_id = create_csv(js_data)
    params = {'uuid': unique_id}
    return jsonify(params)


# 原有项目方法，将结果画到canvas上
@app.route('/plot/<imgdata>')
def plot(imgdata):
    data = [float(i) for i in imgdata.strip('[]').split(',')]
    data = np.reshape(data, (200, 200))
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.axis('off')
    axis.imshow(data, interpolation='nearest')
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


# 原有画图项目方法，给前端传递过来的text生成id
def create_csv(text):
    unique_id = str(uuid.uuid4())
    with open('images/' + unique_id + '.csv', 'a') as file:
        file.write(text[1:-1] + "\n")
    return unique_id


# 原有画图项目方法，根据id获取保存的text内容
def get_file_content(uuid):
    with open('images/' + uuid + '.csv', 'r') as file:
        return file.read()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
