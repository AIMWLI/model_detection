import base64

from flask_tools import MetaClientSender
import cv2

class A(metaclass=MetaClientSender):
    HOST = "localhost"
    Port = 8001
    tag = 'test'
    def sameport(self, x): pass
class B(metaclass=MetaClientSender):
    HOST = "localhost"
    Port = 8002
    tag = 'test'
    def sameport(self, x): pass
class C(metaclass=MetaClientSender):
    HOST = "localhost"
    Port = 8003
    tag = 'test'
    def sameport(self, x): pass
    def parse_image(self, img):pass
    def parse_str(self, base64str):pass


if __name__ == '__main__':

    a = A()
    print(a.sameport(1))#, __passwd="xiangyunOCR#1"))
    # print(a.g(2))#, __passwd="xiangyunOCR#1"))
    b = B()
    print(b.sameport(2))#, __passwd="xiangyunOCR#1"))
    image = cv2.imread('./IMG_2369.jpg')
    image = image[:200, :200, ...]
    import numpy as np
    image = np.asarray(image, np.uint8)
    print(image.shape)
    # a = 'abc'.encode('utf-8')
    # b = base64.b64encode(a)
    # print(a, b)
    # print(A().parse_str(base64str=b))

