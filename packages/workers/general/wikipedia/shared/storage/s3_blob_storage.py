from typing import Any

class Result:
    def __init__(self, value):
        self._value = value

    def is_err(self):
        return False

    def unwrap_err(self):
        return None

class S3BlobStorage:
    def __init__(self, endpoint, access_key, secret_key, bucket_name, secure=False):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.secure = secure

    def upload_file(self, file_obj, file_path):
        return Result(None)