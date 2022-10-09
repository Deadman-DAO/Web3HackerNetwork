import hashlib


def md5_hash(string):
    ret_val = None
    try:
        ret_val = hashlib.md5(string.encode('utf-8')).hexdigest()
    except Exception as e:
        b = bytearray(string, 'unicode-escape')
        ret_val = hashlib.md5(b).hexdigest()
    return ret_val
