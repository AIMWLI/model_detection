import json
import time

import numpy as numpy
import redis
import requests
from django.db.models import Max
from django.http import HttpResponse

from model_detection.conf.redis_pool import pool
from model_detection.models import Record
from model_detection import websocket
redis_template = redis.Redis(connection_pool=pool)


def detection(request):
    #     去连接池中获取连接
    # 设置值
    if request.method == "GET":
        return HttpResponse("Hello None ! ")
    elif request.method == 'POST':
        json_data = json.loads(request.body)
        source = json_data['source']
        image = json_data['imageBase64']
        # 1. 查询缓存权重记录
        record_cache = redis_template.hget("record", source)
        if record_cache is None:
            # 2. 查询数据库记录
            record_query_set = Record.objects.annotate(max=Max("weight")). \
                filter(deleted=0, source=source).values("id", "weight", "source", "interface")
            # 3. 如果存在放入缓存并调用
            if record_query_set is not None:
                record = record_query_set[0]
                redis_template.hset("record", record["source"], str(record))
                # redis_template.expire("record", 5)
                # direct_req(json_data, record)
                random_req(json_data)
            else:
                random_req(json_data)
        else:
            # direct_req(json_data, record_cache)
            random_req(json_data)

        # 缓存命中，直接调用paddle
        # 调用paddle
        # [i for i in a if i in b]
        # request
        return HttpResponse("Hello world ! ")
        # return HttpResponse(json.dumps({'rows': response}), content_type="application/json")


# def save_record(record: Record):
#     Record.save(record)

def direct_req(json_data: json, record: str):
    record = json.loads(str)
    r = requests.post("url" + '/' + record['interface'],
                      data={'source': json_data['source'], 'img': json_data['imageBase64']})
    res = json.loads(r.text)
    content = res["content"]
    return content


def random_req(json_data: json):
    result = None
    smembers = redis_template.smembers("interfaces")
    if not smembers:#len(smembers) == 0:
        interfaces_query_set = list(Record.objects.order_by().values('interface').distinct().filter(deleted=0))

        print(interfaces_query_set)
        # interfaces2 = Record.objects.order_by().values('interface').distinct().values('interface')
        # interfaces = Record.objects.distinct("interface").values("interface")
        # redis_template.sadd("interfaces",*list(interfaces_query_set))
        # interfaces = []
        # for i in interfaces_query_set:
        #     interfaces.append(i["interface"])
        interfaces = [i['interface'] for i in interfaces_query_set]
        redis_template.sadd("interfaces", *interfaces)
        random_list = numpy.random.choice(interfaces, size=len(interfaces), replace=False)
    else:
        print("-------")
        random_list = numpy.random.choice(list(smembers), size=len(smembers), replace=False)
    for i in random_list:
        r = requests.post("url" + '/i', data={'source': json_data['source'], 'img': json_data['imageBase64']})
        res = json.loads(r.text)
        content = res["content"]
        if content is None: continue
        result = content
        record = Record(create_time=time.time(), update_time=time.time(), interface=i, source=json_data['source'])
        record.save()
    return result

# 2、
# (1)
# requests.post方法调三方接口（用的是data）
# r = requests.post(url + 'company/add_friend/', data={'id': zid, 'com_key': com_key})
# # 这一步将返回值转成json
# key = json.loads(r.text)
#
# (2)
# requests.get方法调三方接口（用的是params）
# r = requests.get(url + 'company/search_user/', params={'id': id, 'pub_key': pub_key})
# # 这一步将返回值转成json
# key = json.loads(r.text)
