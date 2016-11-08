from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from wsato_qiligeer_api.serializers import CreateVmSerializer
import pika

class CreateVm(APIView):
    def get(self, request, format=None):
        if request.GET.get('str'):
            str = request.GET['str']
        else:
            raise exceptions.ValidationError(detail=None)
        serializer = CreateVmSerializer({
            'str': str,
        })
        return Response(serializer.data)

    def post(self, request, format=None):
        if request.data.get('create_vm'):
            create_vm = request.data.get('create_vm')
        else:
            raise exceptions.ValidationError(detail=None)

        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='from_api_to_middleware', durable=True)
        properties = pika.BasicProperties(
                content_type='text/plain',
                delivery_mode=2)
        channel.basic_publish(exchange='',
                              routing_key='from_api_to_middleware',
                              body='create_vm')
        connection.close()

        serializer = CreateVmSerializer({
            'create_vm': 'ok',
        })
        return Response(serializer.data)

    def put(self, request, format=None):
        pass

    def delete(self, request, format=None):
        pass
