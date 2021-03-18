import json
import logging
import re
import requests
from os import environ

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting...")

processor_addr = environ.get('PROCESSOR_ADDR')

with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as f:
  k8s_token = f.read()

def main():
  binds = []

  for k, v in environ.items():
    bind_match = re.match(r'^BIND_(.+)$', k)
    if bind_match:
      binds.append(json.loads(v))

  for b in binds:
    secret_values = {}

    if b.get('template') is None:
      empty_template = True
      template = ""
    else:
      empty_template = False
      template = b.get('template')

    for name in b.get('secrets').split(','):
      resp = requests.post(f"{ processor_addr }/readsecret", json={
        'auth': f"Bearer { k8s_token }",
        'name': name,
        'namespace': b.get('namespace')
      },
      verify='/var/run/secrets/kubernetes.io/serviceaccount/ca.crt')
      if resp.status_code != 200:
        raise Exception(f"Got response { resp.status_code }: { resp.json().get('data') }")

      secret_values[name] = resp.json().get('data')

    for name, secret in secret_values.items():
      for k, v in secret.items():
        if empty_template:
          template += f"{ k }={ v }\n"
        else:
          template.replace(f"{{{{ { name }.{ k } }}}}", v)

    with open(b.get('target'), 'w+') as f:
      f.write(template)

if __name__ == '__main__':
  main()