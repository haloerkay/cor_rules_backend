from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
# from CBA_new.main import get_cba_result,get_preprocess
from CMAR.main import get_cmar_result
from CBANB.main import cross_validate_m1_with_prune,cross_validate_m2_with_prune,get_preprocess


app = Flask(__name__)
CORS(app)

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


# @app.route('/cba', methods=['POST'])
# def get_cba():
#     minsup = request.json['minsup']
#     minconf = request.json['minconf']
#     filename = request.json['filename']
#     ret = get_cba_result(minsup,minconf,filename)
#     return jsonify(ret)

@app.route('/cbam1', methods=['POST'])
def get_cbanbm1():
    minsup = request.json['minsup']
    minconf = request.json['minconf']
    filename = request.json['filename']
    ret = cross_validate_m1_with_prune(filename,minsup,minconf)
    print(1)
    return jsonify(ret)

@app.route('/cbam2', methods=['POST'])
def get_cbanbm2():
    minsup = request.json['minsup']
    minconf = request.json['minconf']
    filename = request.json['filename']
    ret = cross_validate_m2_with_prune(filename,minsup,minconf)
    print(2)
    return jsonify(ret)


@app.route('/cmar', methods=['POST'])
def get_cmar():
    minsup = request.json['minsup']
    minconf = request.json['minconf']
    filename = request.json['filename']
    ret = get_cmar_result(filename,minsup,minconf)
    return jsonify(ret)


if __name__ == '__main__':
    app.run(debug = True)
