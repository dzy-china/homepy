from core.extend.c8pyServer.HttpServer import HttpServer

# 地址
host = "127.0.0.1"

# 端口
port = 5000


def web_call(env, response):
    # 响应状态和响应头
    response('200 OK',
             [
                ('Access-Control-Allow-Origin', "*"),
                ('Access-Control-Allow-Headers', "*"),
                ('Access-Control-Allow-Methods', "*")
             ])
    return ["<div style='color:red; font-size:60px'>Is Here!</div>".encode('utf-8')]


if __name__ == '__main__':
    HttpServer(host=host, port=port, callback=web_call)










