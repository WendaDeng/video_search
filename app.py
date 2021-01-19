from __future__ import print_function

from collections import defaultdict
import os
from datetime import datetime
import time

from flask import Flask, render_template, request, jsonify
from flask import flash, redirect, url_for
from werkzeug.utils import secure_filename
from MEE_demo.predict import predict
from local_retrieval.predictor import FeatureExtrator, LocalRetrieval
from reid_demo.search import detect
from video_ocr.tools.infer.predict_system import OCR

app = Flask(__name__)
app.secret_key = 's3cr3t'
app.debug = True
app._static_folder = os.path.abspath("templates/static/")
app._upload_folder = os.path.abspath("templates/upload")
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'png', 'jpg', 'jpeg', 'gif'}

result_num = 12

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
    tacos_query_dict[line.strip().lower()[:-1]] = idx

# 生成 tacos_video: query_result 字典
tacos_result_dict = defaultdict(list)
with open('tacos_result.txt') as f:
    lines = f.readlines()
for line in lines:
    data = line.strip().split(':')
    tacos_result_dict[data[0]].append(data[1])

# 生成 video_name: prediction_result 字典，用于 video_recognition
video_recog_dict = {}
with open('video_recognition_results.txt') as f:
    lines = f.readlines()
for line in lines:
    data = line.strip().split('-')
    video_recog_dict[data[0]] = data[1]


# 渲染生成基础展示页面
@app.route('/', methods=['GET'])
def index():
    return render_template('layouts/index.html')


@app.route('/video_search', methods=['GET'])
def video_search():
    return render_template('layouts/video_search.html')


@app.route('/video_localize', methods=['GET'])
def video_localize():
    return render_template('layouts/video_localize.html')


@app.route('/video_recognize', methods=['GET'])
def video_recognize():
    return render_template('layouts/video_recognize.html')


@app.route('/video_ocr', methods=['GET'])
def video_ocr():
    return render_template('layouts/video_ocr.html')
    

@app.route('/video_reidentify', methods=['GET'])
def video_reidentify():
    return render_template('layouts/video_reidentify.html')


# 响应页面的请求
@app.route('/search', methods=['POST'])
def search():
    search_data = request.form['search_data'][1:-1].strip().lower()  # 去除多余的双引号 ""
    search_data = search_data[:-1] if search_data[-1] == '.' else search_data
    if not search_data:
        flash('Input string is empty!')
        return render_template('layouts/video_search.html')
    top_k = 12
    current_dir = os.getcwd()
    visual_feat_path = os.path.join(current_dir, 'MEE_demo/data/resnet152_features_pkl/msrvtt_resnet152_features_mee_f4.pkl')
    flow_feat_path = os.path.join(current_dir, 'MEE_demo/data/msrvtt_flow_features_mee_mean.pkl')
    instances_features_path = os.path.join(current_dir, 'MEE_demo/data/instances_bottom_up_features.pkl')
    word2vec_root = os.path.join(current_dir, 'MEE_demo/data/word2vec')
    model_params_root = os.path.join(current_dir, 'MEE_demo/model_params/params_f4_150.pkl')

    # 离线版本代码
    # # 检查查询语句是否对应已有视频及查询结果
    # caption_id = caption_dict[search_data] if search_data in caption_dict else None
    # # 如果存在对应的查询结果，获取事先保存的结果
    # result = result_dict[caption_id].split(':') if caption_id and caption_id in result_dict else None
    # scores, video_names = [], []
    # if result:
    #     video_names = result[0].split(',')[:result_num]
    #     scores = result[1].split(',')[:result_num]
    s = time.time()
    video_names, scores = predict(search_data, top_k, visual_feat_path, flow_feat_path, 
                                instances_features_path, word2vec_root, model_params_root)

    idxs = list(range(result_num))
    params = {'video_names': video_names, 'scores': scores, 'idxs': idxs}
    print('total runtime is :', time.time() - s)
    return jsonify(params)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 若不存在此目录，则创建之
            if not os.path.isdir(app._upload_folder):
                os.makedirs(app._upload_folder)

            file.save(os.path.join(app._upload_folder, filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploaded', methods=['GET', 'POST'])
def uploaded_file():

	return '''
	<!doctype html>
	<title>Uploaded the file</title>
	<h1> File has been Successfully Uploaded </h1>
	'''


@app.route('/localize', methods=['POST'])
def localize():
    localize_str = request.form['localize_str'][1:-1].strip().lower()
    localize_str = localize_str[:-1] if localize_str[-1] == '.' else localize_str
    video_path = os.path.join(app._upload_folder, request.form['filename'][1:-1])
    topn = 10
    current_dir = os.getcwd()
    feat_extractor_model_path = os.path.join(current_dir, 'local_retrieval/c3d/c3d.pickle')
    local_retrieval_model_path = os.path.join(current_dir, 'local_retrieval/tacos.pkl')
    # 离线版本代码
    # query_id = tacos_query_dict[localize_str] if localize_str in tacos_query_dict else None
    # query_result = tacos_result_dict[root + '_' + str(query_id)] if query_id else None
    # print(root + '_' + str(query_id))

    # scores, video_names, start_end = [], [], []
    # if query_result:
    #     query_result.sort(reverse=True)
    #     for result in query_result[:result_num]:
    #         # result: score_rank_start-time_end-time
    #         data = result.split(',')
    #         # origin-video-name_score_start-time_end-time_query-id_rank
    #         video_names.append(root + '_' + data[0] + '_' + data[2] + '_' + data[3] + '_' + str(query_id) + '_' + data[1])
    #         scores.append(data[0])
    #         start_end.append(data[2] + '-' + data[3])

    s = time.time()
    feat_extractor = FeatureExtrator(checkpoint=feat_extractor_model_path,
                                     every_n_frames=16, overlap_ratio=0.5)
    feat_extractor.initialize()
    c3d_feats, duration = feat_extractor.feat_extract(video_path)
    c3d_feats = c3d_feats.squeeze()
    local_retrieval = LocalRetrieval(checkpoint=local_retrieval_model_path,
                                     num_clips=256, clip_stride=2)
    local_retrieval.initialize()
    times = local_retrieval.predict(c3d_feats, localize_str, duration, topn)

    params = {'times': times}
    print('total runtime:', time.time() - s)
    print(params)
    return jsonify(params)


@app.route('/recognize', methods=['POST'])
def recognize():
    filename = request.form['filename'][1:-1]
    print('filename:', filename)
    recog_result = video_recog_dict[filename]
    time.sleep(3)
    print('recog_reuslt:', recog_result)
    scores, class_names = [], []
    if recog_result:
        for result in recog_result.split(','):
            data = result.split(':')
            class_names.append(data[0])
            scores.append(data[1])
    params = {'class_names': class_names, 'scores': scores, 'idxs': list(range(len(scores)))}

    return jsonify(params)


@app.route('/ocr', methods=['POST'])
def ocr():
    video_path = os.path.join(app._upload_folder, request.form['filename'][1:-1])
    current_dir = os.getcwd()
    result_dir = os.path.join(current_dir, 'templates/static/videos/ocr')
    OCR(inp_video=video_path, out_path=result_dir)

    result_name = datetime.now().strftime('%b%d_%H-%M-%S')
    os.system('ffmpeg -i {}/output.mp4 -vcodec h264 {}'.format(
        result_dir, os.path.join(result_dir, result_name)))
    print(result_dir)
    os.system('rm {}/output.mp4'.format(result_dir))
    params = {'result_path': result_name}
    
    return jsonify(params)
        

@app.route('/reid', methods=['POST'])
def reid():
    img_path = os.path.join(app._upload_folder, request.form['img_filename'][1:-1])
    current_dir = os.getcwd()
    os.rename(img_path, os.path.join(app._static_folder, 'imgs/reid', '0001_c1s1_001051_01.jpg'))
    video_path = os.path.join(app._upload_folder, request.form['filename'][1:-1])

    current_dir = os.getcwd()
    image_source = os.path.join(current_dir, 'reid_demo/data')
    result_path = detect(data=os.path.join(current_dir, 'reid_demo/data/coco.data'),
                         weights=os.path.join(current_dir, 'reid_demo/weights/yolov3.pt'), 
                         video_source=video_path,
                         images_source=image_source,
                         output_source=os.path.join(app._static_folder, 'videos/reid'))
    print(result_path)
    dirname, basename = os.path.split(result_path)
    newname = datetime.now().strftime('%b%d_%H-%M-%S') + basename
    os.system('ffmpeg -i {} -vcodec h264 {}'.format(result_path, os.path.join(dirname, newname)))
    os.system('rm {}'.format(result_path))
    params = {'result_path': newname, 'img_path':'0001_c1s1_001051_01.jpg'}

    return jsonify(params)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
