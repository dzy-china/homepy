# copy文件
def copy_file(stream, target, maxread=-1, buffer_size=2 ** 16):
    # 已读读取大小
    size = 0
    while True:
        to_read = buffer_size if maxread < 0 else min(buffer_size, maxread - size)
        # 读文件
        part = stream.read(to_read)
        if not part:
            return size
        # 写文件
        target.write(part)
        size += len(part)


# *** 单个获取请求数据类型以及对应数据概要 ***
# 如, 传入：
# 1. multipart/form-data; boundary=--------------------------453559504720078389149314
# 2. form-data; name="age"
# 3. form-data; name="pic"; filename="\xe5\x8d\x95\xe5\x9b\xbe\xe6\xa0\x87logo-\xe6\xad\xa3\xe6\x96\xb9\xe5\xbd\xa2\xe4\xbf\xae\xe8\xae\xa2\xe7\x89\x88.png"
# 4. image/png
# 5. ""
# 返回类似：
#   1.http请求类型标志:  （'multipart/form-data',{'boundary':'--------------------------356095698376383883309561'})
#   2.普通键值对:  （'form-data',{'name':'age'})
#   3.上传文件键值对信息:  （'form-data',{'name':'pic', 'filename':'tum6.png'})
#   4.上传文件类型信息: （'image/png',{})
#   5.空字符串：（'',{})
def parse_options_header(header: str):
    # 一、获取不带分号':'的请求值，如下请求键值对：
    # 文件类型头标志：Content-Type: image/png
    if ";" not in header:
        return header.strip(), {}

    # 二、获取带冒号':'请求值，如下请求键值对：
    # http请求类型标志: multipart/form-data; boundary=--------------------------356095698376383883309561
    # 普通键值对: form-data; name="age"
    # 上传文件键值对信息: form-data; name="pic"; filename="tum6.png"

    # 2.1. 获取 content_type
    content_type, _ = header.split(";", 1)  # 以';'拆分字符串为列表，仅拆分一次

    # 2.2. 获取 请求头对应的全部键值对
    tail_list = header.strip().split(' ')  # 以空格拆分字符串为列表
    tail_list.pop(0)  # 删除第一个非数据元素
    # 获取每一个键值对
    options = {}
    for tail_list_val in tail_list:
        key, value = tail_list_val.split('=', 1)  # 以第一个'='号拆分字符串为列表
        value = value.rstrip(';')  # 去除尾部分号 ;
        value = value.strip('"')  # 去除两端引号 “
        options[key] = value

    return content_type.strip(), options
