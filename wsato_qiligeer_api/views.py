# coding: utf-8
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from wsato_qiligeer_api.serializers import StatusSerializer
from rest_framework import status
import pika
import json
import dataset

class Vm(APIView):
    def get(self, request, format = None):
        request_get = request.GET
        display_name = request_get.get('name')
        user_id = request_get.get('user_id')
        if display_name == None or user_id == None:
            raise exceptions.ValidationError(detail = None)

        db = dataset.connect('mysql://api_user:apiUser@1115@127.0.0.1/wsato_qiligeer')
        table = db['domains']
        results = table.find_one(display_name = display_name, user_id = user_id)

        if results == None:
            return Response(status = status.HTTP_404_NOT_FOUND)
        else:
            serializer = StatusSerializer({
                'status': results['status'],
            })
            return Response(serializer.data)

    def post(self, request, format = None):
        request_get = request.data
        display_name = request_get.get('name')
        user_id = request_get.get('user_id')
        size = request_get.get('size')
        if display_name == None or user_id == None:
            raise exceptions.ValidationError(detail = None)

        db = dataset.connect('mysql://api_user:apiUser@1115@127.0.0.1/wsato_qiligeer')
        table = db['domains']
        results = table.find_one(display_name = display_name, user_id = user_id)
        if results != None :
            return Response(status = status.HTTP_403_FORBIDDEN)

        # Check disk size
        if size == None:
            size = 10
        else:
            size = int(size)

        vc_servers_table = db['vc_servers']
        results = vc_servers_table.find_one(order_by = '-free_size_gb')
        free_size_gb = int(results['free_size_gb'])

        if free_size_gb < size:
            return Response(status = status.HTTP_503_SERVICE_UNAVAILABLE)

        credentials = pika.PlainCredentials('server1_api', '34FS1Ajkns')
        connection  = pika.BlockingConnection(pika.ConnectionParameters(
                virtual_host = '/server1', credentials = credentials))
        channel = connection.channel()

        channel.queue_declare(queue = 'from_api_to_middleware', durable = True)
        properties = pika.BasicProperties(
                content_type = 'text/plain',
                delivery_mode = 2)

        enqueue_message = {
            'ope'          : 'create',
            'user_id'      : user_id,
            'display_name' : display_name,
            'size'         : size
        }

        channel.basic_publish(exchange = '',
                              routing_key = 'from_api_to_middleware',
                              body = json.dumps(enqueue_message))
        connection.close()
        return Response(status = status.HTTP_202_ACCEPTED)

    def put(self, request, format = None):
        pass

    def delete(self, request, format = None):
        request_get = request.data
        display_name = request_get.get('name')
        user_id = request_get.get('user_id')

        if display_name == None or user_id == None:
            raise exceptions.ValidationError(detail = None)

        db = dataset.connect('mysql://api_user:apiUser@1115@127.0.0.1/wsato_qiligeer')
        table = db['domains']
        results = table.find_one(display_name = display_name, user_id = user_id)
        if results == None :
            return Response(status = status.HTTP_404_NOT_FOUND)

        if results['status'] == 'destroy':
            return Response(status = status.HTTP_406_NOT_ACCEPTABLE)

        credentials = pika.PlainCredentials('server1_api', '34FS1Ajkns')
        connection  = pika.BlockingConnection(pika.ConnectionParameters(
                virtual_host = '/server1', credentials = credentials))
        channel = connection.channel()

        channel.queue_declare(queue = 'from_api_to_middleware', durable = True)
        properties = pika.BasicProperties(
                content_type = 'text/plain',
                delivery_mode = 2)

        enqueue_message = {
            'ope'          : 'destroy',
            'user_id'      : user_id,
            'display_name' : display_name
        }

        channel.basic_publish(exchange = '',
                              routing_key = 'from_api_to_middleware',
                              body = json.dumps(enqueue_message))
        connection.close()
        return Response(status = status.HTTP_202_ACCEPTED)
