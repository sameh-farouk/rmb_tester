# rmb_tester
for testing purposes, you can use either RMB_Tester or RMB_echo or both to quickly test communication between multiple RMB

## installation:
- clone the repo
- create a new env
```py
python3 -m venv venv
```
- activate the new env
```py
source ./venv/bin/activate
```
- install dependencies
```py
pip install -r requirements.txt
```

## RMB_tester
will automate crafting number of messages to be sent to one or multiple destinations.
the number of messages and the command, data, retry count and dest list are configurable through the command line. it will wait from the correct number of responses and report some statics. make sure there is a process running on dest side that can handle this command and respond back or use RMB_echo for this.

example:
```py
python3 ./rmb_tester.py --dest 41 55
```

for all optional args see
```py
python3 ./rmb_tester.py -h
```

## RMB_echo (message handler)
will automate handling the messages coming to $queue and respond with same message back to the source.

example:
```py
python3 ./msg_handler.py
```

or specify the command/queue to handle the messages from
```py
python3 ./msg_handler.py --queue helloworld
```

for all optional args see
```py
python3 ./msg_handler.py -h
```
