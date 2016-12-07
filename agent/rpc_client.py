#!/usr/bin/env python
import pika
import uuid

class WsatoRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost',
                socket_timeout=300))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, msg):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='from_middleware_to_agent',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=msg)
        while self.response is None:
            self.connection.process_data_events()
        return self.response

wsato_rpc = WsatoRpcClient()

print(" [x] Sending msg")
response = wsato_rpc.call('{"op":"create", "name":"bbb", "os":"centos7", "size":"10"}')
print(" [.] Got %s" % response)
