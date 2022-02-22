import redis

# docker run -itd --name redis --restart always -p 6379:6379  redis --requirepass "xiangyun123"
# docker run -itd --name redis --restart always -p 6380:6379  redis --requirepass "xiangyun123"
# r = redis.Redis(host='localhost', port=6379, db=0, password='xiangyun123')
# r.set('foo', 'bar')
# r.get('foo')
# pool = redis.ConnectionPool(host='localhost', port=6380, db=0, password='xiangyun123',max_connections=256)
pool = redis.ConnectionPool(host='localhost', port=6380, db=0,max_connections=256)
r = redis.Redis(connection_pool=pool)

r.set('foo1', 'bar')
r.get('foo1')

