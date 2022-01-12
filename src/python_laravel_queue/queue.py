from redis import Redis
import json
import module.phpserialize as phpserialize
from pyee import BaseEventEmitter
import uuid
import time

class Queue:

    def __init__(self, client: Redis, 
                 queue: str,
                 driver: str = 'redis',
                 appname: str = 'laravel', prefix: str = '_database_', is_queue_notify: bool = True, is_horizon: bool = False) -> None:
        self.driver = driver
        self.client = client
        self.queue = queue
        self.appname = appname
        self.prefix = prefix
        self.is_queue_notify = is_queue_notify
        self.is_horizon = is_horizon
        self.ee = BaseEventEmitter()

    def push(self, name: str, dictObj: dict):
        if self.driver == 'redis':
            self.redisPush(name, dictObj)

    def listen(self):
        if self.driver == 'redis':
            self.redisPop()

    def handler(self, f=None):
        def wrapper(f):
            self.ee._add_event_handler('queued', f, f)
        if f is None:
            return wrapper
        else:
            return wrapper(f)

    def redisPop(self):
        err, data = self.client.blpop(
            self.appname + self.prefix + 'queues:' + self.queue, 60000)
        obj = json.loads(data)
        command = obj['data']['command']
        raw = phpserialize.loads(command, object_hook=phpserialize.phpobject)

        self.ee.emit(
            'queued', {'name': obj['data']['commandName'], 'data': raw._asdict()})

        if self.is_horizon: # TODO
            pass 
        
        if self.is_queue_notify:
            self.client.blpop(
                self.appname + self.prefix + 'queues:' + self.queue + ':notify', 60000)

        self.redisPop()

    def redisPush(self, name: str, dictObj: dict, timeout: int = None, delay: int = None):
        command = phpserialize.dumps(phpserialize.phpobject(name, dictObj))
        data = {
        "uuid": str(uuid.uuid4()),
        "job": 'Illuminate\\Queue\\CallQueuedHandler@call',
        "data": {
            "commandName": name,
            "command": command.decode("utf-8"),
        },
        "timeout": timeout,
        "id": str(time.time()),
        "attempts": 0,
        "delay": delay,
        "maxExceptions": None,
        }
        
        if self.is_queue_notify == False:
            del data['delay']
            del data['maxExceptions']
            data.update({'displayName': name, 'maxTries': None, 'timeoutAt': None})
        
        self.client.rpush(
            self.appname + self.prefix + 'queues:' + self.queue, json.dumps(data))