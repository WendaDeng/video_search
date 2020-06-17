from __future__ import print_function
from flask import Flask, render_template, make_response
from flask import redirect, request, jsonify, url_for

import io
import os
import uuid
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import random

app = Flask(__name__)
app.secret_key = 's3cr3t'
app.debug = True
app._static_folder = os.path.abspath("templates/static/")

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


@app.route('/', methods=['GET'])
def index():
    title = 'Video Search'
    return render_template('layouts/index.html',
                           title=title)


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


@app.route('/search', methods=['POST'])
def search():
    js_data = request.form['search_data'][1:-1]
    caption_id = caption_dict[js_data] if js_data in caption_dict else None
    result = result_dict[caption_id].split(':') if caption_id else None
    idxs = list(range(10))
    scores, video_names = [], []
    if result:
        video_names = result[0].split(',')[:10]
        scores = result[1].split(',')[:10]

    print('scores:', scores)
    print('video_names: ', video_names)
    params = {'video_names': video_names, 'scores': scores, 'idxs': idxs}
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
