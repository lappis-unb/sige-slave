import socket
import threading
import queue
import pickle
import time

# message from slave format
# {
#     'protocol':
#     'ip':
#     'port':
#     'content':
# }

# response format
# {
#     'status':
#     'content'
# }


MSG_SIZE = 1024



def send_udp_messages(messages, address, response=True):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    for message in messages:
        send_udp_message(message, address, s, response)
    return response

def send_udp_message(message, address, s = None, response=True):
    if(s is None):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
    s.sendto(message, address)
    if(response):
        response, transductor = s.recvfrom(MSG_SIZE)

        return response

def send_tcp_messages(messages, address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    s.connect(address)
    print("Here2")
    responses = []
    for message in messages:
        print(pickle.dumps(message))
        s.send(message)
        response, transductor = s.recvfrom(MSG_SIZE)
        print("Here2.5")
        print(pickle.dumps(response))
        responses.append(response)
    s.close()
    return responses

def worker(message_queue):
    while(True):
        aux = message_queue.get()
        print("Here7")
        print(aux)
        message = aux[0]
        sender = aux[1]
        print("Here1.5")
        print(message)
        transductor = (message['ip'], message['port'])
        try:
            if(message['protocol'] == 'UDP'):
                transductor_response = send_udp_message(
                    message['content'], transductor)
                response = {}
                response['status'] = 1
                response['content'] = transductor_response
            elif(message['protocol'] == 'TCP'):
                transductor_response = send_tcp_message(
                    message['content'], transductor)
                response = {}
                response['status'] = 1
                response['content'] = transductor_response
            else:
                response['status'] = 0
                response['content'] = 'Unknown protocol'
        except Exception as e:
            response = {}
            response['status'] = 0
            response['content'] = e
        print("Here3")
        print(response)
        print(sender)
        response = pickle.dumps(response)
        try:
            send_udp_message(response, sender,response=False) 
        except:
            pass
        print("Here4")
        print(response)

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', 6071))

    # This is a dict with all the message queues that uses the ip of 
    # the reciver as key and the queue of messages to that reciver as value
    message_queues = {}

    while(True):
        message, sender = s.recvfrom(MSG_SIZE)
        message = pickle.loads(message)
        print("Here1")
        print(message)
        queue_identifier = message['ip']

        if(message_queues.__contains__(message['ip'])):
            ip = message_queues[queue_identifier]
            ip.put([message, sender])

        else:
            message_queues[message['ip']] = queue.Queue()

            message_queues[message['ip']].put([message, sender])

            t = threading.Thread(target=worker, args=(
                message_queues[message['ip']],))
            t.start()
