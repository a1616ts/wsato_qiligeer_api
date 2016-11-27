# coding: utf-8
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import status
import pika
import json
import dataset
from wsato_qiligeer_api.models import Domains, VcServers
from django.core import serializers
import simplejson

class Vm(APIView):
    def get(self, request, format = None):
        request_get = request.GET
        display_name = request_get.get('name')
        user_id = request_get.get('user_id')
        if user_id == None:
            raise exceptions.ValidationError(detail = None)

        if display_name == None:
            domains = Domains.objects.filter(user_id = user_id)
            if len(domains) < 1 :
                return Response(status = status.HTTP_404_NOT_FOUND)
            else:
                results = []
                for domain in domains:
                    results.append({
                        'name': domain.display_name,
                        'status': domain.status,
                        'size': domain.size,
                        'ram': domain.ram,
                        'vcpus': domain.vcpus,
                        'ip': domain.ip,
                        'key_path': domain.key_path,
                    })
                return Response(results)

        else:
            domain = Domains.objects.filter(user_id = user_id, display_name = display_name)[0]
            if domain == None:
                return Response(status = status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'name': domain.display_name,
                    'status': domain.status,
                    'size': domain.size,
                    'ram': domain.ram,
                    'vcpus': domain.vcpus,
                    'ip': domain.ip,
                    'key_path': domain.key_path,
                })

    def post(self, request, format = None):
        request_get = request.data

        display_name = request_get.get('name')
        user_id = request_get.get('user_id')
        size = request_get.get('size')
        ram = request_get.get('ram')
        vcpus = request_get.get('vcpus')

        if display_name == None or user_id == None:
            raise exceptions.ValidationError(detail = None)

        domain = Domains.objects.filter(display_name = display_name, user_id = user_id)[0]
        if domain != None :
            return Response(status = status.HTTP_403_FORBIDDEN)

        # Check disk size
        if size == None:
            size = 10
        else:
            size = int(size)

        vc_server = VcServers.objects.order_by('-free_size_gb')[0]
        free_size_gb = int(vc_server['free_size_gb'])

        if free_size_gb + size < size:
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
            'size'         : size,
            'ram'          : ram,
            'vcpus'        : vcpus
        }

        channel.basic_publish(exchange = '',
                              routing_key = 'from_api_to_middleware',
                              body = json.dumps(enqueue_message))
        connection.close()
        return Response(status = status.HTTP_202_ACCEPTED)

    def put(self, request, format = None):
        request_get = request.data
        display_name = request_get.get('name')
        user_id = request_get.get('user_id')
        op = request_get.get('op')

        if display_name == None or user_id == None or op == None:
            raise exceptions.ValidationError(detail = None)

        domain = Domains.objects.filter(display_name = display_name, user_id = user_id)[0]
        if domain == None :
            return Response(status = status.HTTP_404_NOT_FOUND)

        # TODO 確認
        if (domain.status == 'inactive' and op =='suspend') and (domain.status == 'active' and op =='resume') and (domain.status == 'running' and op =='start'):
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
            'op'          : op,
            'user_id'      : user_id,
            'display_name' : display_name
        }

        channel.basic_publish(exchange = '',
                              routing_key = 'from_api_to_middleware',
                              body = json.dumps(enqueue_message))
        connection.close()
        return Response(status = status.HTTP_202_ACCEPTED)

    def delete(self, request, format = None):
        request_get = request.data
        display_name = request_get.get('name')
        user_id = request_get.get('user_id')
        op = request_get.get('op')

        if display_name == None or user_id == None:
            raise exceptions.ValidationError(detail = None)

        domain = Domains.objects.filter(display_name = display_name, user_id = user_id)[0]
        if domain == None:
            return Response(status = status.HTTP_404_NOT_FOUND)

        if domain.status == 'destroy':
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
            'op'          : 'destroy',
            'user_id'      : user_id,
            'display_name' : display_name
        }

        channel.basic_publish(exchange = '',
                              routing_key = 'from_api_to_middleware',
                              body = json.dumps(enqueue_message))
        connection.close()
        return Response(status = status.HTTP_202_ACCEPTED)
