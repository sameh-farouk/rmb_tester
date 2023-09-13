from dataclasses import dataclass
import uuid
import time
from timeit import default_timer as timer
from alive_progress import alive_bar
import json
import base64
import redis
import argparse
import string    
import random

@dataclass
class Message:
    version: int
    ref: str
    command: str
    expiration: int
    data: str
    #tags: str
    twin_dst: list
    reply_to: uuid.UUID
    schema: str
    epoch: time.struct_time
    err: dict
    twin_src: string

    def to_json(self):
        msg_dct = {
        "ver": self.version,
        "ref": self.ref,
        "cmd": self.command,
        "exp": self.expiration,
        "dat": base64.b64encode(self.data.encode('utf-8')).decode('utf-8'),
        # "tag": self.tags,
        "dst": self.twin_dst,
        "ret": self.reply_to,
        "shm": self.schema,
        "now": self.epoch,
    }
        return json.dumps(msg_dct)

    @classmethod
    def from_json(cls, json_data):
        msg_dict = json.loads(json_data)
        return cls(
            version=msg_dict.get('ver'),
            ref=msg_dict.get('ref'),
            command=msg_dict.get('cmd'),
            expiration=msg_dict.get('exp'),
            data=base64.b64decode(msg_dict.get('dat')).decode('utf-8'),
            reply_to=msg_dict.get('ret'),
            schema=msg_dict.get('shm'),
            epoch=msg_dict.get('now'),
            err= msg_dict.get('err'),
            twin_src=msg_dict.get('src'),
            twin_dst=msg_dict.get('dst')
        )

# init new message
def new_message(command: str, twin_dst: list, data: dict = {}, expiration: int = 120):
    version = 1
    reply_to = str(uuid.uuid4())
    schema = "application/json"
    epoch = int(time.time())
    err = {"code": 0, "message": ""}
    ref = ""
    # tags = ""
    return Message(version, ref, command, expiration, data, twin_dst, reply_to, schema, epoch, err, "")

def send_all(messages):
    responses_expected = 0
    return_queues = []
    with alive_bar(len(messages), title=f'Sending ..', title_length=12) as bar:
        for msg in messages:
            r.lpush("msgbus.system.local", msg.to_json())
            responses_expected += len(msg.twin_dst)
            return_queues += [msg.reply_to]
            bar()
    return responses_expected, return_queues

def wait_all(responses_expected, return_queues, timeout=20):
        responses = []
        err_count = 0
        success_count = 0
        with alive_bar(responses_expected, title=f'Waiting ..', title_length=12) as bar:
            for i in range(responses_expected):
                result = r.blpop(return_queues, timeout=timeout)
                if not result:
                    break
                response = Message.from_json(result[1])
                responses.append(response)
                if response.err is not None:
                    err_count += 1
                    bar.text('received an error ❌')
                else:
                    success_count += 1
                    bar.text(f'received a response from twin {response.twin_src} ✅')
                bar()
        return responses, err_count, success_count

def main():
    global r
    parser = argparse.ArgumentParser("RMB_tester")
    parser.add_argument("-d", "--dest", help="list of twin ids(integer) to send message/s to. (required at least one)", nargs='+', type=int, required=True)
    parser.add_argument("-n", "--count", help="count of messages to send. defaults to 25.", type=int, default=25)
    parser.add_argument("-c", "--command", help="command which will handle the message. defaults to 'testme'", type=str, default='testme')
    parser.add_argument("--data", help="data to send. defaults to random chars.", type=str, default=''.join(random.choices(string.ascii_uppercase + string.digits, k = 56)) )
    parser.add_argument("-e", "--expiration", help="message expiration time in seconds. defaults to 120.", type=int, default=120)
    parser.add_argument("-t", "--timeout", help="client will give up waiting if no new message received during the amount of seconds. defaults to 20.", type=int, default=20)
    parser.add_argument("--short", help="omit responses output and shows only the stats.", action='store_true')
    parser.add_argument("-p", "--redis-port", help="redis port for the instance used by rmb-peer", type=int, default=6379)
    args = parser.parse_args()
    r = redis.Redis(host='localhost', port=args.redis_port, db=0)
    # print(args)
    msg = new_message(args.command, args.dest, data=args.data, expiration=args.expiration)
    # print(msg.to_json())
    msgs = [msg] * args.count
    start = timer()
    responses_expected, return_queues = send_all(msgs)
    responses, err_count, success_count = wait_all(responses_expected, return_queues, timeout=args.timeout)
    elapsed_time = timer() - start
    no_responses = responses_expected - len(responses) 
    print("=======================")
    print("Summary:")
    print("=======================")
    print(f"sent: {len(msgs)}")
    print(f"expected_responses: {responses_expected}")
    print(f"received_success: {success_count}")
    print(f"received_errors: {err_count}")
    print(f"no response errors (client give up): {no_responses}")
    print(f"elapsed time: {elapsed_time}")
    print("=======================")
    if not args.short:
        print("Responses:")
        print("=======================")
        for response in responses:
            print(response)
        print("=======================")
        print("Errors:")
        print("=======================")
        for response in responses:
            if response.err is not None:
                print(f"Error: {response['err']}")
                print(f"From Twin: {response['src']}")


if __name__ == "__main__":
    NUM_RETRY = 3
    r = None
    main()
