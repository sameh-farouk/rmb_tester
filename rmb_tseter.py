from dataclasses import dataclass
from email import message
from http.client import responses
from urllib import response
import uuid
import time
from timeit import default_timer as timer
from alive_progress import alive_bar
from alive_progress import alive_it
import json
import base64
import redis

@dataclass
class Message:
    version: int
    id: str
    command: str
    expiration: int
    retry: int
    data: str
    twin_src: int
    twin_dst: list
    retqueue: uuid.UUID
    schema: str
    epoch: time.struct_time
    err: str

    def to_json(self):
        msg_dct = {
        "ver": self.version,
        "uid": self.id,
        "cmd": self.command,
        "exp": self.expiration,
        "try": self.retry,
        "dat": base64.encodebytes(self.data.encode('utf-8')).decode('utf-8'),
        "src": self.twin_src,
        "dst": self.twin_dst,
        "ret": self.retqueue,
        "shm": self.schema,
        "now": self.epoch,
        "err": self.err
    }
        return json.dumps(msg_dct)
    
    @classmethod
    def from_json(cls, json_data):
        msg_dict = json.loads(json_data)
        return cls(
            msg_dict['ver'],
            msg_dict['uid'],
            msg_dict['cmd'],
            msg_dict['exp'],
            msg_dict['try'],
            msg_dict['dat'],
            msg_dict['src'],
            msg_dict['dst'],
            msg_dict['ret'],
            msg_dict['shm'],
            msg_dict['now'],
            msg_dict['err'],
        ) 

# init new message
def new_message(command: str, twin_dst: list, data: dict = {}, expiration: int = 120, retry: int = 3):
    version = 1
    id =  str(uuid.uuid4())
    twin_src = 0
    retqueue = str(uuid.uuid4())
    schema = ""
    epoch = int(time.time())
    err = ""
    return Message(version, id, command, expiration, retry, data, twin_src, twin_dst, retqueue, schema, epoch, err)

def send_all(messages):
    responses_expected = 0
    return_queues = []
    with alive_bar(len(messages), title=f'Sending ..', title_length=12) as bar:
        for msg in messages:
            r.lpush("msgbus.system.local", msg.to_json())
            responses_expected += len(msg.twin_dst)
            return_queues += [msg.retqueue]
            bar()
    return responses_expected, return_queues

def wait_all(responses_expected, return_queues):
        responses = []
        err_count = 0
        success_count = 0
        with alive_bar(responses_expected, title=f'Waiting ..', title_length=12) as bar:
            for i in range(responses_expected):
                result = r.blpop(return_queues)
                response = json.loads(result[1])
                responses.append(response)
                if response["err"]:
                    err_count += 1
                    bar.text('received an error ❌')
                else:
                    success_count += 1
                    bar.text(f'received a response from twin {response["src"]} ✅')
                bar()
        return responses, err_count, success_count

        
        



def main():
    msg = new_message("testme", [41], data = "GA7OPN4A3JNHLPHPEWM4PJDOYYDYNZOM7ES6YL3O7NC3PRY3V3UX6ANM", retry=3)
    msgs = [msg] * 25
    start = timer()
    responses_expected, return_queues = send_all(msgs)
    responses, err_count, success_count = wait_all(responses_expected, return_queues)
    elapsed_time = timer() - start
    print("=======================")
    print("Summary:")
    print("=======================")
    print(f"sent: {len(msgs)}")
    print(f"expected_responses: {responses_expected}")
    print(f"received_success: {success_count}")
    print(f"received_errors: {err_count}")
    print(f"elapsed time: {elapsed_time}")
    print("=======================")
    print("Responses:")
    print("=======================")
    for response in responses:
        print(response)
    print("=======================")
    print("Errors:")
    print("=======================")
    for response in responses:
        if response["err"]:
            print(response["err"])
        

if __name__ == "__main__":
    NUM_RETRY = 3
    r = redis.Redis(host='localhost', port=6379, db=0)
    main()
