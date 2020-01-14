import socket
import threading
import queue
import pickle


# [ip, protocolo, sender, message]

def worker(q):
    print(q)
    while(True):
        r = q.get()
        print(r)

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('localhost', 1996))
    q = {} 
    while(True):
        r, a = s.recvfrom(1024)
        r = pickle.loads(r)
        print(r)
        if(q.__contains__(r['ip'])):
            print(1)
            ip = q[r['ip']]
            ip.add(r)

        else:
            print(2)
            q[r['ip']] = queue.Queue()
            q[r['ip']].put(r)
            t = threading.Thread(target=worker,args=(q[r['ip']],))
            t.start()
        

