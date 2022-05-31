import redis
import json
from rmb_tseter import Message
import time

if __name__ == "__main__":
    r = redis.Redis(host='localhost', port=6379, db=0)
    while True:
        result = r.blpop('msgbus.testme')
        msg = Message.from_json(result[1])
        msg.epoch = int(time.time())
        msg.twin_dst, msg.twin_src = msg.twin_src, msg.twin_dst
        r.lpush(msg.retqueue, msg.to_json())
