from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from CMAR.main import get_cmar_result,cross_validate_cmar
from CBANB.main import cba_m1_prune,cba_m2_prune,get_preprocess,cross_validate_m1,cross_validate_m2
from server.APR.main import apr,cross_validate_apr

app = Flask(__name__)
CORS(app)
app.config['preprocess'] = ''
@app.route('/upload', methods=[ 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        upload_folder = 'dataset'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        return "success"
    else:
        return 'file not uploaded'

@app.route('/pre_process/<file>', methods=['GET'])
def get_pre_process(file):
   ret = get_preprocess(file)
   return jsonify(ret)

def convert_sets_to_lists(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {key: convert_sets_to_lists(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets_to_lists(item) for item in obj]
    else:
        return obj


@app.route('/cbam1', methods=['POST'])
def get_cbam1():
    minsup = request.json['minsup']
    minconf = request.json['minconf']
    filename = request.json['filename']
    ret = cba_m1_prune(filename,minsup,minconf)
    return jsonify(ret)
@app.route('/cbaapr', methods=['POST'])
def get_cbaapr():
    minsup = request.json['minsup']
    minconf = request.json['minconf']
    filename = request.json['filename']
    ret = apr(filename,minsup,minconf)
    return jsonify(ret)

@app.route('/cbam2', methods=['POST'])
def get_cbam2():
    minsup = request.json['minsup']
    minconf = request.json['minconf']
    filename = request.json['filename']
    ret = cba_m2_prune(filename,minsup,minconf)
    return jsonify(ret)


@app.route('/cmar', methods=['POST'])
def get_cmar():
    minsup = request.json['minsup']
    minconf = request.json['minconf']
    filename = request.json['filename']
    ret = get_cmar_result(filename, minsup, minconf)
    converted_ret = convert_sets_to_lists(ret)
    return jsonify(converted_ret)

@app.route('/test',methods=['POST'])
def get_test():
    ret = []
    minsup = request.json['minsup']
    minconf = request.json['minconf']
    filename = request.json['filename']
    ret.append(cross_validate_m1(filename, minsup, minconf))
    ret.append(cross_validate_m2(filename, minsup, minconf))
    ret.append(cross_validate_apr(filename, minsup, minconf))
    ret.append(cross_validate_cmar(filename, minsup, minconf))
    print(ret)
    return jsonify(ret)


if __name__ == '__main__':
    app.run(debug = True)
