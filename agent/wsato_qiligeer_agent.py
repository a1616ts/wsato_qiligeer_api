#!/usr/bin/env python
import pika
#from MyKVM import *

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='from_middleware_to_agent')


def on_request(ch, method, props, body):

    print("Receive %s" % body)

    #kvm = MyKVM("centos2")
    #kvm.MyKVM_create()

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                     props.correlation_id),
                     body='Done')
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='from_middleware_to_agent')

print(" [x] Awaiting RPC requests")
channel.start_consuming()
