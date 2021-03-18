import json
import logging
import sys

from flask import Flask, request, jsonify
from os import environ, path
from ssl import SSLContext, PROTOCOL_TLSv1_2

sys.path.append(path.join(path.dirname(path.abspath(__file__)), "../"))

from controller.main import get_controllers
from controller.exceptions import ESKException
from injector.webhook import mutate
from injector.processor import ESKProcessor

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

s_controller, sb_controller = get_controllers()
processor = ESKProcessor(s_controller)

processor_addr = environ.get('PROCESSOR_ADDR')
init_image = environ.get('INIT_IMAGE')

if processor_addr is None:
  raise ESKException(500, "Processor addr is invalid.")

if init_image is None:
  raise ESKException(500, "Init image is invalid.")

@app.route('/mutate', methods=['POST'])
def mutate_webhook():
  allowed, patch = mutate(sb_controller, init_image, processor_addr, request.json["request"])

  admission_response = {
      "allowed": allowed,
      "uid": request.json["request"]["uid"],
      "patch": patch,
      "patchtype": "JSONPatch"
  }
  admissionReview = {
      "response": admission_response
  }

  return jsonify(admissionReview)


@app.route('/readsecret', methods=['POST'])
def read_secret():
  data = json.loads(request.data)

  ret_code, values = processor.process_secret_read(
    data.get('auth'),
    data.get('name'),
    data.get('namespace')
  )

  return jsonify({'data': values }), ret_code


@app.route("/healthz", methods=["GET"])
def health():
  return jsonify()


if __name__ == '__main__':
  cert_path = environ.get('CERT_FILE_PATH')
  key_path = environ.get('CERT_KEY_PATH')

  if cert_path is None or key_path is None:
    app.run('0.0.0.0', 80, threaded=True)
  else:
    context = SSLContext(PROTOCOL_TLSv1_2)
    context.load_cert_chain(cert_path, key_path)

    app.run('0.0.0.0', 443, threaded=True, debug=True, ssl_context=context)