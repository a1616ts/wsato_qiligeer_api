#!/usr/bin/env python
# coding:UTF-8

import string
import subprocess
import pika
import json
import os.path
import socket

from RepeatedTimer import RepeatedTimer
from time import sleep

import logging
import logging.config

virsh_cmd_sh = '/root/agent/virsh_cmd.sh'
ssh_cmd_sh = '/root/agent/dcm_ssh.sh'

pubfile = '/root/agent/pub/vm.pub'

dcm_user = 'solar'
dcm_ip = '192.168.1.1'
dcm_port = '52051'
dcm_key = '/root/agent/grp1.pem'
dcm_pub_dir = '/home/solar/agent/pub'
dcm_pub_file = '/home/solar/agent/pub/vm.pub'

logging.config.fileConfig("log.conf")
logger = logging.getLogger()

isSend = False

def getPubKey(name):
    logger.info("getPubKey")
    try:
        if(getState(name) != 'active'):
            #virsh_with_name('start', name)
            cmd = "virsh start %s" % (name)
            p = subprocess.Popen(cmd, shell=True)
            p.communicate()


        cmd = "%s getip %s" % (virsh_cmd_sh, name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        stdout_data, stderr_data = p.communicate()
        ip_addr = stdout_data.decode('utf-8')
        logging.info("ip %s", ip_addr)
        socket.inet_aton(ip_addr)
        if( os.path.isfile(pubfile) ) :
            sendPubKey(name, ip_addr)

    except Exception as e:
        logging.traceback(e)


def startTimer(name):
    isSend = True
    rt = RepeatedTimer(90, getPubKey, name)
    try:
        sleep(600)
    finally:
        rt.stop()

def sendPubKey(name, ip):
    logger.info("sendPubKey")
    msg = {'name', 'ipv4_address', 'sshkey_path', 'error'}
    logger.info("isSend %d", isSend)
    if not isSend:
        return

    try:
        cmd = "%s %s %s %s %s %s %s" % (ssh_cmd_sh, 
                               dcm_user, dcm_ip, 
                               dcm_port, dcm_key, 
                               pubfile, dcm_pub_dir)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        #stdout_data, stderr_data = p.communicate()
        #logging.info("ssh %s %s", stdout_data, stderr_data)
        res = subprocess.check_output(cmd, shell=True)
        logging.info("ssh %s", res)
        msg['name'] = str(name)
        msg['ipv4_address'] = str(ip)
        msg['sshkey_path'] = str(dcm_pub_file)
        msg['error'] = 'success'
        credentials = pika.PlainCredentials('server2_agent', 'joe2ts4g6aS')
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                          '192.168.1.1', 5672, '/server2', credentials))
        channel = connection.channel()
        channel.queue_declare(queue='from_middleware_to_agent', durable = True)
        channel.basic_publish(exchange='',
                      routing_key='from_agent_to_middleware',
                      body=json.dumps(msg))
        connection.close()
        isSend = False
    except Exception as e:
        logging.traceback(e)

def getState(name):
    logger.info("getState")
    try:
        cmd = "%s getstate %s" % (virsh_cmd_sh, name)
        #p = subprocess.Popen(cmd, shell=True)
        #stdout_data, stderr_data = p.communicate()
        #res = stdout_data.decode('utf-8')
        res = subprocess.check_output(cmd, shell=True)
        logging.info("state %s", res.decode('utf-8'))
        if res.decode('utf-8') in {'running'} :
            st = 'active'
        elif res.decode('utf-8') in {'paused'} :
            st = 'inactive'
        elif res.decode('utf-8') in {'shut off'} :
            st = 'stop'
        else:
            st = 'destroy'
    except Exception as e:
        logging.traceback(e)
        st = ''
    logger.info("st=%s" % st)
    return st


def virt_install(op, name, os, size, vcpu, ram):
    logger.info("virt_install")
    try:
        cmd = "%s %s %s %s %s %s %s" % (virsh_cmd_sh, op, name, os, size, vcpu, ram)
        logger.info(cmd)
        p = subprocess.Popen(cmd, shell=True)
        stdout_data, stderr_data = p.communicate()
        if (p.returncode == 0) :
            startTimer(name)
            if( os.path.isfile(pubfile) ) :
                os.remove(pubfile)
            msg = {
                'state' : 'starting',
                'error' : 'success'
            }
        else:
            msg = {
                'error' : 'failed'
            }
    except Exception as e:
        logging.traceback(e)
        msg = {
            'error' : 'failed'
        }
    logger.info(json.dumps(msg))
    return msg

def virsh_with_name(op, name):
    logger.info("virsh_with_name")
    msg = {'state', 'error'}
    try:
        cmd = "%s %s %s" % (virsh_cmd_sh, op, name)
        p = subprocess.Popen(cmd, shell=True)
        stdout_data, stderr_data = p.communicate()
        if (p.returncode == 0) :
            msg['error'] = 'success'
            st = getState(name)
            msg['state'] = st
        else:
            msg['error'] = 'failed'
    except Exception as e:
        logging.traceback(e)
        msg['error'] = 'failed'
    logger.info(json.dumps(msg))
    return msg

def on_request(ch, method, props, body):
    decoded_json = json.loads(body.decode('utf-8'))
    op = decoded_json['op']
    name = decoded_json['name']
    logger.info("%s %s" % (op, name))
    if op == 'create' :
        os = decoded_json['os']
        size = decoded_json['size']
        vcpu = decoded_json['vcpus']
        ram = decoded_json['ram']
        logger.info("%s %s %s %s %s %s" % (op, name, os, size, vcpu, ram))
        msg = virt_install(op, name, os, size, vcpu, ram)
        on_response(ch, method, props, msg)
    elif op in {'resume','suspend', 'destroy', 'close', 'undefine', 'start', 'getstate'} :
        msg = virsh_with_name(op, name)
        on_response(ch, method, props, msg)
    else:
        logger.error("invalid operation")

def on_response(ch, method, props, msg):
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                     props.correlation_id),
                     body=json.dumps(msg))
    ch.basic_ack(delivery_tag = method.delivery_tag)


credentials = pika.PlainCredentials('server2_agent', 'joe2ts4g6aS')
connection = pika.BlockingConnection(pika.ConnectionParameters(
        '192.168.1.1', 5672, '/server2', credentials))
channel = connection.channel()
channel.queue_declare(queue='from_middleware_to_agent', durable = True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='from_middleware_to_agent', no_ack=True)

logger.error(" [x] Awaiting RPC requests")
channel.start_consuming()
