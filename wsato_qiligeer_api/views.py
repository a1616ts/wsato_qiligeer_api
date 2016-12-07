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
        data = request.GET
        display_name = data.get('name')
        user_id = data.get('user_id')
        if user_id == None:
            return Response(status = status.HTTP_403_FORBIDDEN)

        if display_name == None:
            domains = Domains.objects.filter(user_id = user_id)
            if domains.count() < 1 :
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
            domains = Domains.objects.filter(user_id = user_id, display_name = display_name)
            if domains.count() < 1:
                return Response(status = status.HTTP_404_NOT_FOUND)
            else:
                domain = domains[0]
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
        data = request.data
        name = data.get('name')
        user_id = data.get('user_id')
        size = data.get('size')
        ram = data.get('ram')
        vcpus = data.get('vcpus')
        os = data.get('os')
        if name == None or user_id == None:
            raise exceptions.ValidationError(detail = None)

        count = Domains.objects.filter(display_name = name, user_id = user_id).count()
        if 0 < count :
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
        for server in VcServers.objects.raw('SELECT * FROM vc_servers'):
            if 0 < int(server.free_size_gb) - size and 0 < int(server.free_cpu_core) and 0 < int(server.free_memory_byte) :
                target_server = server
                break

        if target_server == None:
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
        data = request.data
        name = data.get('name')
        user_id = data.get('user_id')
        op = data.get('op')

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
