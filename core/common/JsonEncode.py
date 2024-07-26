import json


# 通用 json序列化方式
# 一般json序列化方式： json.dumps(dic)
# 通用json序列化方式： json.dumps(dic, cls=JsonEncode)
class JsonEncode(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, (dict, list, tuple, int, float, bool)):
            return str(obj)
        else:  # 如果数据包含 python 自定义类对象形式
            return json.JSONEncoder.default(self, obj)
