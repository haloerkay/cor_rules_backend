from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from CBA_new.main import get_cba_result
from CMAR.main import get_cmar_result


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


@app.route('/cba', methods=['POST'])
def get_cba():
    minsup = request.json['minsup']
    minconf = request.json['minconf']
    filename = request.json['filename']
    ret = get_cba_result(minsup,minconf,filename)
    return jsonify(ret)
  # return ret
  # ret = get_cba_result(file)
  # return jsonify(ret)



# @app.route('/cmar/<file>', methods=['GET'])
def get_cmar(file):
   ret = get_cmar_result(file)
   return jsonify(ret)


if __name__ == '__main__':
    app.run(debug = True)
