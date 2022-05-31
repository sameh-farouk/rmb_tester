import redis
from rmb_tester import Message
import time
import argparse

def listen(q):
    while True:
        result = r.blpop(f'msgbus.{q}')
        msg = Message.from_json(result[1])
        msg.epoch = int(time.time())
        msg.twin_dst, msg.twin_src = msg.twin_src, msg.twin_dst
        r.lpush(msg.retqueue, msg.to_json())

if __name__ == "__main__":
    parser = argparse.ArgumentParser("RMB_echo")
    parser.add_argument("--queue", help="redis queue name. defaults to 'testme'",  type=str, default='testme')
    args = parser.parse_args()

    r = redis.Redis(host='localhost', port=6379, db=0)
    print("RMB_echo")
    print(f"handling command msgbus.{args.queue}")
    listen(args.queue)

    
