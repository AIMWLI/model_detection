import base64
import urllib.request
from functools import wraps
import numpy as np
import cv2
from PIL import Image
import json


def check_url(basetag):
    def _check_url(func):
        @wraps(func)
        def __check_url(self, *args, **kwargs):
            self.url_tag = urllib.parse.urljoin(self.url, basetag)
            return func(self, *args, **kwargs)

        return __check_url

    return _check_url


class RenameFunction(object):
    def __init__(self, func, funcname):
        self.func = func
        self.funcname = funcname

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __str__(self):
        funcid = hex(id(self.func))
        return f"<function {self.funcname} at {funcid}>"


class ClientSender(object):
    def __init__(self, url):
        self.url = url
        self.url_tag = None

    @staticmethod
    def _getByte(path):
        if isinstance(path, str):
            with open(path, 'rb') as f:
                img_byte = base64.b64encode(f.read())
        else:
            ret, buf = cv2.imencode(".jpg", path)
            img_bin = Image.fromarray(np.uint8(buf)).tobytes()
            img_byte = base64.b64encode(img_bin)
        img_str = img_byte.decode('ascii')
        return img_str

    def send_request(self, tag, header=None, **kwargs):
        if header is None: header = dict()
        url_tag = urllib.parse.urljoin(self.url, tag)
        data = dict()
        for name, value in kwargs.items():
            if isinstance(value, np.ndarray):
                data[name] = ClientSender._getByte(value)
            else:
                data[name] = value
        data = urllib.parse.urlencode(data).encode("utf-8")
        res = urllib.request.Request(url_tag, data=data, headers=header)
        res = urllib.request.urlopen(res).read().decode("utf-8")
        res = json.loads(res)
        if res['error_stats'] == 0:  # sucess
            return eval(res['results'])
        raise Exception(f"{res['error'], res.get('params', '')}")


class MetaClientSender(type):

    @staticmethod
    def _getdictattr(d, attr, ignorecapital=True):
        attr_ = d.get(attr, None)
        if attr_ is not None or ignorecapital is False:
            return attr_
        for k in d:
            if k.lower() == attr.lower():
                return d[k]
        return None

    def __new__(cls, class_name, class_parents, class_attr):
        host = MetaClientSender._getdictattr(class_attr, 'HOST')
        if host is None: raise ValueError('missing host in MetaClientSender.')
        port = MetaClientSender._getdictattr(class_attr, 'PORT')
        if port is None: raise ValueError('missing port in MetaClientSender.')
        tag = MetaClientSender._getdictattr(class_attr, 'TAG')
        if tag is None: raise ValueError('missing tag in MetaClientSender.')
        class_attr['clientsender'] = cs = ClientSender(url=f'http://{host}:{port}')

        def get_func(tag, name, co_varnames=None):
            def _func(*args, **kwargs):
                if args and co_varnames is not None:
                    for k, v in zip(co_varnames, args):
                        kwargs[k] = v
                try:
                    return cs.send_request(tag=f'/{tag}/{name}', **kwargs)
                except urllib.error.HTTPError as e:
                    error_info = (f"""{host}:{port}/{tag}/{name} connection error."""
                                  """ Plz check the server whether it is supportted.""")
                    raise urllib.error.URLError(error_info) from e
                finally:
                    pass

            return RenameFunction(func=_func, funcname=f"{class_name}.{name}")

        for name, value in class_attr.items():
            if name.startswith("__"): continue
            if not callable(value): continue
            co_varnames = None
            try:
                co_varnames = class_attr[name].__code__.co_varnames
            except AttributeError as e:
                pass
            if len(co_varnames)>0 and co_varnames[0] == 'self': co_varnames = co_varnames[1:]
            class_attr[name] = get_func(tag, name, co_varnames)


        def __getattribute__(this, attr):
            if attr in class_attr:
                return class_attr[attr]
            return get_func(tag, attr)

        class_attr['__getattribute__'] = __getattribute__
        return super(MetaClientSender, cls).__new__(cls, class_name, class_parents, class_attr)


# class OcrClient(object, metaclass=MetaClientSender):
#     Host = '172.16.16.50'
#     Port = 8000
#     Tag = 'cnocr'

    # def get_pos_and_text(self, img) -> [(tuple, tuple, float, str)]: pass
    #
    # def is_correct(self, res) -> bool: pass
    #
    # def parse(self, img) -> str: pass
    #
    # def parse_auto_scale(self, img) -> str: pass
    #
    # def parse_date(self, img) -> str: pass
    #
    # def parse_num(self, img) -> str: pass
    #
    # def parse_single_line(self, img) -> str: pass
    #
    # def parse_with_std(self, img) -> str: pass
    #
    # def parse_with_std_box(self, img) -> (list, str): pass
    #
    # def pr_parse(self, img) -> [(str, float)]: pass
    #
    # def pr_parse_single_line(self, img) -> [(str, float)]: pass


if __name__ == '__main__':
    img = cv2.imread(r'/Users/shaneleo/workspace/python-code/cnocr_train/cnocr-master/examples/00010991.jpg')
    cst = OcrClient()
    res = cst.parse_auto_scaled(img=img, is_single_line=True)
    print(res)
    res = cst.parse_with_std(img=img)
    print(res)
