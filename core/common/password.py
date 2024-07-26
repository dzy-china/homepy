import hashlib
import hmac
import uuid


#  md5加密
def md5(msg: any) -> str:
    msg = str(msg)  # 加密消息
    return hashlib.new('md5', msg.encode('utf-8')).hexdigest()


#  sha1加密
def sha1(msg: any) -> str:
    msg = str(msg)  # 加密消息
    return hashlib.new('sha1', msg.encode('utf-8')).hexdigest()


#  md5 带秘钥 加密
def md5_hmac(msg: any) -> str:
    key = b'1129881228@qq.com'  # 密钥
    msg = str(msg)  # 加密消息
    md5_obj = hmac.new(key, msg.encode('utf-8'), 'MD5')  # 指定加密类型
    return md5_obj.hexdigest()  # 获取摘要(密文)


#  uuid
def get_uuid(msg=None) -> str:
    if msg:
        msg = str(msg)  # 加密消息
        return uuid.uuid5(uuid.NAMESPACE_DNS, msg).hex  # 采用的是sha1，生成固定的字符串
    else:
        return uuid.uuid1().hex  # 是基于mac地址，时间戳，随机数来生成唯一的uuid，可以保证全球唯一性
