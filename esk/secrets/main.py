import base64
import json
import random
import string

from os import remove
from hashlib import sha256
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def get_nonce():
  chars = string.ascii_letters + string.digits
  result_str = "".join(random.choice(chars) for _ in range(12))

  return result_str


class SecretsManager:
  def __init__(self, enc_key):
    self.__cipher = AESGCM(enc_key)


  def create(self, path, values):
    with open(sha256(path.encode('utf-8')).hexdigest(), 'w+') as f:
      f.write(self.encrypt(values))


  def delete(self, path):
    remove(path)


  def get(self, path, values):
    with open(sha256(path.encode('utf-8')).hexdigest(), 'w+') as f:
      return json.loads(self.decrypt(values).decode('utf-8'))


  def encrypt(self, values):
    nonce = get_nonce()
    return nonce + self.__cipher.encrypt(nonce, json.dumps(values).encode('utf-8'), b"")


  def decrypt(self, ciphertext):
    return self.__cipher.decrypt(ciphertext[:12], ciphertext[12:], b"")
