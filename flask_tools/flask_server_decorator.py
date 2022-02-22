from flask import Flask, jsonify, request, make_response, send_file
import base64
from functools import wraps
import os
import cv2
import numpy as np
try:
    from logger.logger import logger
except ModuleNotFoundError as e:
    class Logger(object):
        def __getattr__(self, item): return lambda *args, **kwargs: args
    logger = Logger()
AUTH = ""#"xiangyunOCR#1"
def auto_route(app, rule=None, tag=None, methods=None, image_args=None, base64_args=None):
    if tag is not None:
        while tag.startswith('/'):
            tag = tag[1:]
        while tag.endswith('/'):
            tag = tag[:-1]
    if methods is None:
        methods = ['POST', 'GET']
    elif isinstance(methods, str):
        assert methods in ['POST', 'GET'], f'unknown methods for app.route {methods}'
        methods = [methods]
    if isinstance(image_args, str):
        image_args = [image_args]
    if isinstance(base64_args, str):
        base64_args =[base64_args]
    if base64_args is None: base64_args = list()
    def _auto_route(func):
        if rule is None:
            _rule = f'/{func.__name__}' if tag is None else f'/{tag}/{func.__name__}'
        else:
            _rule = rule.replace('<__funcname__>', func.__name__)

        @wraps(func)
        def __auto_route(**kwargs):
            logger.info(f"{request.remote_addr} visits.")
            if not kwargs:
                for rv in request.values.dicts:
                    #print('dict(rv)', dict(rv))
                    kwargs.update(dict(rv))
                    
                    logger.info(f"params are {[(k, v) for k, v in kwargs.items() if (k != 'img' and k not in base64_args)]}")
                    
            for name in kwargs:
                if isinstance(kwargs[name], list):kwargs[name] = ''.join(kwargs[name])
                if kwargs[name] in ['True', 'False', 'None']:
                    kwargs[name] = eval(kwargs[name])
            
            if AUTH:
                auth = kwargs.get('__passwd', None)
                if auth is None or auth != AUTH:
                    return jsonify({'error_stats': 0,
                                    'results': "'Good Luck!'"})
            kwargs.pop('__passwd', None)

            if image_args is not None:
                _image_kwargs = dict()
                for k in image_args:
                    img_str = request.values.get(k, None)
                    if img_str is None:
                        return jsonify({'error': str(TypeError(f'missing declared required image argument {k}')),
                                        'error_stats': 1})
                    elif os.path.isfile(img_str):
                        _image_kwargs[k] = cv2.imread(img_str)
                    else:  # np.array base64 encoding data
                        img_decode_ = img_str.encode('ascii')
                        img_decode = base64.b64decode(img_decode_)
                        img_np_ = np.frombuffer(img_decode, np.uint8)
                        img = cv2.imdecode(img_np_, cv2.COLOR_RGB2BGR)
                        _image_kwargs[k] = img
                        logger.info(f"got image param with shape - {img.shape}")
                kwargs.update(_image_kwargs)
            if base64_args is not None:
                _base64_args = dict()
                for k in base64_args:
                    base64_str = request.values.get(k, None)
                    if base64_str is None:
                        return jsonify({'error': str(TypeError(f'missing declared required base64 argument {k}')),
                                        'error_stats': 1})
                    else:
                        decode_str = base64.b64decode(base64_str.encode('utf-8')).decode('utf-8')
                        _base64_args[k] = decode_str
                        logger.info(f"got base64 param with key - {k}, and decoded value - {decode_str[:10]}")
                kwargs.update(_base64_args)
            try:
                res = func(**kwargs)
            except Exception as e:
                error_info = {'params': 'Plz check the params of function <%s>. The kwargs are %s' % (
                    func.__name__, {k: (v, type(v)) for k, v in kwargs.items()}),
                              'error': f"{type(e)}: {e}",
                              'error_stats': 1}
                logger.error(f"{error_info}")
                return jsonify(error_info)
            return jsonify({'error_stats': 0,
                            'results': repr(res)})
        logger.info(f'use url:{_rule} to visit <function> {__auto_route.__name__}.')
        return app.route(_rule, methods=methods)(__auto_route)

    return _auto_route


class FlaskAppDecorator(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'decorator'):
            cls.decorator = super(FlaskAppDecorator, cls).__new__(cls)
            cls.app = Flask(__name__)
        return cls.decorator

    def __init__(self):
        self.rule = None
        self.tag = None
        self.methods = None
        self.image_args = None
        self.base64_args = None

    def run(self, *args, **kwargs):
        self.app.run(*args, **kwargs)

    def set_route_params(self, rule=None, tag=None, methods=None, image_args=None, base64_args=None):
        self.rule = rule
        self.tag = tag
        self.methods = methods
        self.image_args = image_args
        self.base64_args = base64_args

    def auto_route(self, rule=None, tag=None, methods=None, image_args=None, base64_args=None):
        rule = self.rule if rule is None else rule
        tag = self.tag if tag is None else tag
        methods = self.methods if methods is None else methods
        image_args = self.image_args if image_args is None else image_args
        base64_args = self.base64_args if base64_args is None else base64_args
        return auto_route(self.app, rule, tag, methods, image_args, base64_args)

    def auto_route_func_list(self, funclist: list, rule=None, tag=None, methods=None, image_args=None, base64_args=None):
        return [self.auto_route(rule, tag, methods, image_args, base64_args)(func) for func in funclist]

    def auto_route_class(self, cls, rule=None, tag=None, methods=None, image_args=None, base64_args=None):
        for attr_name in dir(cls):
            if attr_name.startswith('_'): continue
            if attr_name == 'run': continue
            func = getattr(cls, attr_name)
            if not callable(func): continue
            self.auto_route(rule, tag, methods, image_args, base64_args)(func)


def try_auto_tag(x, a):
    res = dict()
    if isinstance(a, str):
        res.update({'a': a})
    elif a is not None:
        from matplotlib import pyplot as plt
        plt.imshow(a)
        plt.show()
    res.update({'x': int(x) + 1})
    return int(x) + 1
#
#
# dec = FlaskApp()
#
#
# # http://localhost:8000/license/try_auto_tag_1?x=100
# @auto_route(app=dec.app, tag='/license', image_args='a')
# def try_auto_tag_1(x: str, a=None):
#     return try_auto_tag(x, a)
#
#
# # http://localhost:8000/license/try_auto_tag_2/100/a_is_a_string
# @dec.auto_route(tag='/license/', rule='/license/<__funcname__>/<x>/<a>')
# def try_auto_tag_2(x: str, a=None):
#     return try_auto_tag(x, a)
#
#
# def try_auto_tag_4(x: str, a=None):
#     return try_auto_tag(x, a)
#
#
# def try_auto_tag_5(x: str, a=None):
#     return try_auto_tag(x, a)
#
#
# def try_auto_tag_6(x: str, a=None):
#     return try_auto_tag(x, a)
#
# class TryAutoTag(object):
#     def __init__(self):pass
#
#     def try_auto_tag_7(self, x: str, a=None):
#         return try_auto_tag(x, a)
#
#     def try_auto_tag_8(self, x: str, a=None):
#         return try_auto_tag(x, a)
#
#
# if __name__ == '__main__':
#     # app_v1_1.run(host='127.0.0.1', port=8000)
#     dec.auto_route_func_list([try_auto_tag_4, try_auto_tag_5, try_auto_tag_6], tag='/license', image_args='a')
#     dec.auto_route_class(TryAutoTag(), tag='/license', image_args='a')
#     dec.run(host='127.0.0.1', port=8000)
