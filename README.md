# RMB tools (CLI tools/scripts)

You can fins here CLI tools and scripts that can be used for testing and benchmarking [RMB](https://github.com/threefoldtech/rmb-rs). You can use either RMB_Tester, RMB_echo, or both to quickly test the communications over RMB.

## Installation:
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

## Usage:
RMB tools comprise two Python programs that can be used independently or in conjunction with each other.

### RMB_Tester
RMB_Tester is a CLI tool that serves as an RMB client to automate the process of crafting a specified number of test messages to be sent to one or more destinations. The number of messages, command, data, destination list, and other parameters can be configured through the command line. The tool will wait for the correct number of responses and report some statistics.

Please ensure that there is a process running on the destination side that can handle this command and respond back or use RMB_echo for this purpose.

example:
```sh
# We sending to two destinations
# The default test command will be used and can be handled by RMB_echo process
python3 ./rmb_tester.py --dest 41 55
```

to just print the summary use `--short` option

to override default command use the `--command`
```sh
# The `rmb.version` command will be handled by RMB process itself
python3 ./rmb_tester.py --dest 41 --command rmb.version
```

for all optional args see
```sh
python3 ./rmb_tester.py -h
```

### RMB_Echo (message handler)
This tool will automate handling the messages coming to $queue and respond with same message back to the source and display the count of processed messages.

example:
```sh
python3 ./msg_handler.py
```

or specify the redis queue (command) to handle the messages from
```sh
python3 ./msg_handler.py --queue helloworld
```

for all optional args see
```sh
python3 ./msg_handler.py -h
```

## Recipes:
- Test all online nodes (based on up reports) to ensure that they are reachable over RMB
```sh
# The online_nodes.sh script will output the ids of the online nodes in the dev net using the gridproxy API.
python3 ./rmb_tester.py --dest $(./scripts/online_nodes.sh) -c "rmb.version"
```
