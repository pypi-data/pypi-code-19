from io import BytesIO

from qiniu import put_data, Auth
from qiniu.utils import etag_stream


def upload_data(access_token, access_key, bucket, data, filename=None, postfix=None):
    q = Auth(access_token, access_key)
    bucket_name = bucket
    if filename:
        key = filename
    else:
        key = etag_stream(BytesIO(data))
        if postfix:
            key = f'{key}.{postfix}'
    token = q.upload_token(bucket_name, key, 3600)
    return put_data(token, key, data)
