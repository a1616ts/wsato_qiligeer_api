from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from wsato_qiligeer_api.serializers import StatusSerializer
from wsato_qiligeer_api.serializers import ResultSerializer
import pika
import json
import dataset

class Vm(APIView):
    def get(self, request, format = None):
        if request.GET.get('name'):
            name = request.GET['name']
        else:
            raise exceptions.ValidationError(detail=None)

        # TODO Should we use Django model?
        db = dataset.connect('mysql://root@127.0.0.1/wsato_qiligeer')
        table = db['domains']
        results = table.find_one(vm_name = name)

        serializer = StatusSerializer({
            'status': results['status'] if results != None else 'no vm',
        })
        return Response(serializer.data)

    def post(self, request, format = None):
        if name = request.data.get('name'):
            name = request.data.get('name')
        else:
            raise exceptions.ValidationError(detail = None)

        enqueue_message = {
            'ope'  : 'create',
            'name' : name
        }

        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host = 'localhost'))
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
