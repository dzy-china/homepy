# 文件上传配置
class UploadConfig:
    # 上传路径前缀
    # 注：
    # 1.upload_path_prefix值为空，默认上传到与入口文件 main.py 同级目录下upload目录
    # 2.upload_path_prefix值不为空，则上传到： upload_path_prefix目录/upload
    # 3.尾部路径分隔符可不用添加
    upload_path_prefix = 'E:\\project\\nodejs\\nuxt3-c8py-admin\\public\\'

    # 上传的文件可访问域名，作为文件上传成功后的第二个参数返回
    domain = 'http://192.168.2.210:5500'
