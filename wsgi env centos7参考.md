## wsgi 请求参数env centos7参考
```json
{
	'REQUEST_METHOD': 'POST',
	'PATH_INFO': '/hello/word',
	'REQUEST_URI': '/hello/word?keyword=zhangsan&description=lisi',
	'QUERY_STRING': 'keyword=zhangsan&description=lisi',
	'SERVER_PROTOCOL': 'HTTP/1.1',
	'SCRIPT_NAME': '',
	'SERVER_NAME': 'a788062',
	'SERVER_PORT': '5000',
	'UWSGI_ROUTER': 'http',
	'REMOTE_ADDR': '114.85.82.161',
	'REMOTE_PORT': '48166',
	'HTTP_USER_AGENT': 'ApiPOST Runtime +https://www.apipost.cn',
	'HTTP_ACCEPT': '*/*',
	'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br',
	'HTTP_CONNECTION': 'keep-alive',
	'HTTP_HOST': '139.196.145.155:5000',
	'CONTENT_TYPE': 'multipart/form-data; boundary=--------------------------609614173876930108218026',
	'CONTENT_LENGTH': '56869',
	'wsgi.input': < uwsgi._Input object at 0x7fa9bd8cf150 > ,
	'wsgi.file_wrapper': < built - in function uwsgi_sendfile > ,
	'wsgi.version': (1, 0),
	'wsgi.errors': < _io.TextIOWrapper name = 2 mode = 'w'
	encoding = 'UTF-8' > ,
	'wsgi.run_once': False,
	'wsgi.multithread': True,
	'wsgi.multiprocess': False,
	'wsgi.url_scheme': 'http',
	'uwsgi.version': b '2.0.20',
	'uwsgi.core': 0,
	'uwsgi.node': b 'a788062'
}
```