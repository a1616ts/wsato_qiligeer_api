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
            return Response(status = status.HTTP_403_FORBIDDEN)

        if display_name == None:
            domains = Domains.objects.filter(user_id = user_id)
            if len(domains) < 1 :
                return Response(status = status.HTTP_404_NOT_FOUND)
            else:
                results = []
                count = 1
                for domain in domains:
                    results.append({
                        'id' : count,
                        'name': domain.display_name,
                        'os': domain.os,
                        'status': domain.status,
                        'size': domain.size,
                        'ram': domain.ram,
                        'vcpus': domain.vcpus,
                        'ipv4_address': domain.ipv4_address,
                        'sshkey_path': domain.sshkey_path,
                        'create_date': domain.create_date,
                        'update_date': domain.update_date,
                    })
                    count = count + 1
                return Response(results)

        else:
            domain = Domains.objects.filter(user_id = user_id, display_name = display_name)[0]
            if domain == None:
                return Response(status = status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'name': domain.display_name,
                    'os': domain.os,
                    'status': domain.status,
                    'size': domain.size,
                    'ram': domain.ram,
                    'vcpus': domain.vcpus,
                    'ipv4_address': domain.ipv4_address,
                    'sshkey_path': domain.sshkey_path,
                    'create_date': domain.create_date,
                    'update_date': domain.update_date,
                })

    def post(self, request, format = None):
        request_get = request.data
        name = request_get.get('name')
        user_id = request_get.get('user_id')
        size = request_get.get('size')
        ram = request_get.get('ram')
        vcpus = request_get.get('vcpus')
        os = request_get.get('os')
        if name == None or user_id == None:
            raise exceptions.ValidationError(detail = None)

        domain = Domains.objects.filter(display_name = name, user_id = user_id)[0]
        if domain != None :
           return Response(status = status.HTTP_403_FORBIDDEN)

        if size == None:
            size = 10
        else:
            size = int(size)

        if ram == None:
            ram = 1024
        else:
            ram = int(ram)

        if vcpus == None:
            vcpus = 1
        else:
            vcpus = int(vcpus)

        target_server = None
        t_size = 0
        t_core = 0
        t_ram = 0
        for server in VcServers.objects:
            t_size = int(vc_server.free_size_gb) - size
            t_core = int(vc_server.free_cpu_core) - vcpus
            t_ram = int(vc_server.free_memory_byte) - ram
            if 0 < t_size and  0 < t_core and 0 < t_ram:
                target_server = server

        if target_server == None
             return Response(status = status.HTTP_503_SERVICE_UNAVAILABLE)

        credentials = pika.PlainCredentials('server1_dcm', '8nfdsS12gaf')
        connection  = pika.BlockingConnection(pika.ConnectionParameters(
                virtual_host = '/server1', credentials = credentials))
        channel = connection.channel()
        channel.queue_declare(queue = 'from_api_to_middleware', durable = True)
        properties = pika.BasicProperties(
                content_type = 'text/plain',
                delivery_mode = 2)

        enqueue_message = {
            'op'          : 'create',
            'user_id'      : user_id,
            'name'         : name,
            'size'         : size,
            'ram'          : ram,
            'vcpus'        : vcpus,
            'os'           : os
        }
        channel.basic_publish(exchange = '',
                              routing_key = 'from_api_to_middleware',
                              body = json.dumps(enqueue_message))
        connection.close()
        return Response(status = status.HTTP_202_ACCEPTED)

    def put(self, request, format = None):
        request_get = request.data
        name = request_get.get('name')
        user_id = request_get.get('user_id')
        op = request_get.get('op')

        if name == None or user_id == None or op == None:
            raise exceptions.ValidationError(detail = None)

        domain = Domains.objects.filter(display_name = name, user_id = user_id)[0]
        if domain == None :
            return Response(status = status.HTTP_404_NOT_FOUND)

        if (op == 'resume' and domain.status != 'inactive') \
            or (op == 'suspend' and domain.status != 'active') \
            or (op == 'start' and domain.status != 'stop')  \
            or (op == 'stop' and domain.status not in [ 'active', 'inactive']):
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
            'op'      : op,
            'user_id' : user_id,
            'name'    : name
        }

        channel.basic_publish(exchange = '',
                              routing_key = 'from_api_to_middleware',
                              body = json.dumps(enqueue_message))

        connection.close()
        return Response(status = status.HTTP_202_ACCEPTED)

    def delete(self, request, format = None):
        print(request.data)
        data = request.data
        display_name = data.get('name')
        user_id = data.get('user_id')
        op = data.get('op')

        if display_name == None or user_id == None:
            raise exceptions.ValidationError(detail = None)

        domain = Domains.objects.filter(display_name = display_name, user_id = user_id)[0]
        if domain == None:
            return Response(status = status.HTTP_404_NOT_FOUND)

        if domain.status != 'close':
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
