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

        # TODO Should we use Django's model?
        db = dataset.connect('mysql://api_user:apiUser@1115@127.0.0.1/wsato_qiligeer')
        table = db['domains']
        results = table.find_one(display_name = display_name, user_id = user_id)

        if results == None :
            return Response(status = status.HTTP_404_NOT_FOUND)

        # TODO Check server's free space

        serializer = StatusSerializer({
            'status': results['status'],
        })
        return Response(serializer.data)

    def post(self, request, format = None):
        request_get = request.data
        display_name = request_get.get('name')
        user_id = request_get.get('user_id')

        if display_name == None or user_id == None:
            raise exceptions.ValidationError(detail = None)

        # TODO Validation
        db = dataset.connect('mysql://api_user:apiUser@1115@127.0.0.1/wsato_qiligeer')
        table = db['domains']
        results = table.find_one(display_name = display_name, user_id = user_id)
        if results != None :
            return Response(status = status.HTTP_403_FORBIDDEN)

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
            'display_name' : display_name
        }

        channel.basic_publish(exchange = '',
                              routing_key = 'from_api_to_middleware',
                              body = json.dumps(enqueue_message))
        connection.close()
        return Response(status = status.HTTP_202_ACCEPTED)

    def put(self, request, format = None):
        # TODO
        # Receive suspend and resume, close
        # Enqueue to from_api_to_middleware
        pass

    def delete(self, request, format = None):
        # TODO
        pass
