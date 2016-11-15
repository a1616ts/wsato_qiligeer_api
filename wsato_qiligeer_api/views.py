from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from wsato_qiligeer_api.serializers import StatusSerializer
from wsato_qiligeer_api.serializers import ResultSerializer
from rest_framework import status
import pika
import json
import dataset

class Vm(APIView):
    def get(self, request, format = None):
        if request.GET.get('vm_name'):
            vm_name = request.GET['vm_name']
        else:
            raise exceptions.ValidationError(detail=None)

        # TODO Use Django Model?
        db = dataset.connect('mysql://api_user:apiUser@1115@127.0.0.1/wsato_qiligeer')
        table = db['domains']
        results = table.find_one(vm_name = vm_name)

        if results == None :
            return Response(status = status.HTTP_404_NOT_FOUND)
        else :
            serializer = StatusSerializer({
                'status': results['status'],
            })
            return Response(serializer.data)

    def post(self, request, format = None):
        if request.data.get('vm_name'):
            vm_name = request.data.get('vm_name')
        else:
            raise exceptions.ValidationError(detail = None)

        enqueue_message = {
            'ope'  : 'create',
            'name' : vm_name
        }

        credentials= pika.PlainCredentials('server1_api', '34FS1Ajkns')
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                virtual_host = '/server1', credentials = credentials))
        channel = connection.channel()

        channel.queue_declare(queue = 'from_api_to_middleware', durable = True)
        properties = pika.BasicProperties(
                content_type = 'text/plain',
                delivery_mode = 2)
        channel.basic_publish(exchange = '',
                              routing_key = 'from_api_to_middleware',
                              body = json.dumps(enqueue_message))
        connection.close()

        serializer = ResultSerializer({
            'result': 'ok',
        })
        return Response(serializer.data)

    def put(self, request, format = None):
        # TODO
        # Receive suspend and resume, close
        # Enqueue to from_api_to_middleware
        pass

    def delete(self, request, format = None):
        # TODO
        pass
