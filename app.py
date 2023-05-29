from flask import Flask, request, send_file
import methods
import os.path


# methods.reconstruct('1', '2')
app = Flask(__name__)
allow_headers = "Origin, Expires, Content-Type, X-E4M-With, Authorization"
file_directory = "./obj/"
http_response_header = {"Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": allow_headers}


@app.route("/reconstruct", methods=['POST', 'OPTIONS'])
def reconstruct():
    if request.method == 'POST':
        slice_info = request.json
        size, index, dataset_name = slice_info['size'], slice_info['index'], slice_info['datasetName']
        dataset = methods.get_data_from_slice_info(size, index)
        methods.reconstruct(dataset, dataset_name)
        return {"code": 200, "data": True}, 200, http_response_header
    if request.method == 'OPTIONS':
        return {"str": "ok"}, 202, http_response_header


@app.route("/obj/<objname>")
def obj(objname):
    return send_file(file_directory + objname, as_attachment=True,
                     attachment_filename='test.obj'), 200, http_response_header


@app.route("/obj/<random_number>/<objname>")
def obj(random_number, objname):
    return send_file(file_directory + objname, as_attachment=True,
                     attachment_filename='test.obj'), 200, http_response_header


@app.route("/query/<dataset_name>", methods=['GET', 'OPTIONS'])
def query_dataset_name(dataset_name):
    print(dataset_name)
    res = {"code": 200}
    if os.path.isfile(file_directory + dataset_name + ".obj"):
        res["data"] = True
    else:
        res["data"] = False
    return res, 200, http_response_header


@app.route("/process", methods=['GET', 'OPTIONS'])
def get_process():
    process = methods.get_process()
    return {"data": process, "code": 200}, 200, http_response_header
