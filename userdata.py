#userdata.py

import logging
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import json
import os

class UserDataManager:
    def __init__(self, data_file):
        self.data_file = data_file
        self.user_data = self.load_data()
        self.key = self.generate_encryption_key()
        self.cipher = self.create_aes_cipher()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.user_data, f)

    def set_user_progress(self, user_id, progress_data):
        encrypted_data = self.encrypt_data(json.dumps(progress_data))
        if user_id in self.user_data:
            self.user_data[user_id]['progress'] = encrypted_data
        else:
            self.user_data[user_id] = {'progress': encrypted_data}
        self.save_data()

    def get_user_progress(self, user_id):
        if user_id in self.user_data and 'progress' in self.user_data[user_id]:
            encrypted_data = self.user_data[user_id]['progress']
            return json.loads(self.decrypt_data(encrypted_data))
        return {}

    def create_aes_cipher(self):
        key = get_random_bytes(16)
        return AES.new(key, AES.MODE_CBC)

    def encrypt_data(self, data):
        cipher = self.create_aes_cipher()
        data_bytes = data.encode('utf-8')
        data_bytes_padded = pad(data_bytes, 16)
        encrypted_data = cipher.encrypt(data_bytes_padded)
        return b64encode(cipher.iv + encrypted_data).decode('utf-8')

    def decrypt_data(self, data):
        cipher = self.create_aes_cipher()
        data_bytes = b64decode(data)
        iv = data_bytes[:16]
        encrypted_data = data_bytes[16:]
        cipher_dec = AES.new(cipher.key, AES.MODE_CBC, iv=iv)
        decrypted_data = cipher_dec.decrypt(encrypted_data)
        decrypted_data_unpadded = unpad(decrypted_data, 16)
        return decrypted_data_unpadded.decode('utf-8')

    def set_user_data(self, user_id, data):
        encrypted_data = self.encrypt_data(json.dumps(data))
        self.user_data[user_id] = encrypted_data
        self.save_data()

    def get_user_data(self, user_id):
        if user_id in self.user_data:
            encrypted_data = self.user_data[user_id]
            return json.loads(self.decrypt_data(encrypted_data))
        return None
