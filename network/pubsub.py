"""

"""
#########################################
######## IMPORTS, PATHS, GLOBALS ########
#########################################

import threading
import time
import Queue
import zmq

from thirtybirds_2_0.Network.info import init as network_info_init
network_info = network_info_init()

class Subscription():
    def __init__(self, hostname, remote_ip, remote_port):
        self.hostname = hostname
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.connected = False

class SendQueue(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.queue = Queue.Queue()

    def add_to_queue(self, topic, msg):
        self.queue.put((topic, msg))

    def run(self):
        while True:
            topic, msg = self.queue.get(True)
            self.socket.send_string("%s %s" % (topic, msg))

class PubSub(threading.Thread):
    def __init__(
            self,
            hostname, 
            publish_port, 
            pubsub_callback 
        ):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.publish_port = publish_port
        self.pubsub_callback  = pubsub_callback  
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind("tcp://*:%s" % publish_port)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.subscriptions = {}
        self.sendqueue = SendQueue(self.sub_socket)

    def send(self, topic, msg):
        self.sendqueue.add_to_queue(topic, msg)

    def connect_to_publisher(self, hostname, remote_ip, remote_port):
        if hostname not in self.subscriptions:
            self.subscriptions[hostname] = Subscription(hostname, remote_ip, remote_port)
            self.sub_socket.connect("tcp://%s:%s" % (remote_ip, remote_port))

    def subscribe_to_topic(self, topic):
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, topic)

    def unsubscribe_from_topic(self, topic):
        topic = topic.decode('ascii') # convert to ascii range
        self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, topic)

    def run(self):
        while True:
            incoming_message = self.sub_socket.recv()
            topic, msg = incoming_message.split(' ', 1)
            self.pubsub_callback(topic, msg)

def init(
        hostname, 
        publish_port, 
        pubsub_callback
    ):
    pubsub = PubSub(
        hostname, 
        publish_port, 
        pubsub_callback
    )
    pubsub.start()
    return pubsub
