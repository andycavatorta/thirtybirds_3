"""

"""
#########################################
######## IMPORTS, PATHS, GLOBALS ########
#########################################

import threading
import time
import queue
import zmq

from network.info import init as network_info_init
network_info = network_info_init()

from reports import reports
exceptions = reports.Exceptions() # is there a way for a module to sniff a reference to the file that imports it?

class Subscription():
    def __init__(self, hostname, remote_ip, remote_port):
        try:
            self.hostname = hostname
            self.remote_ip = remote_ip
            self.remote_port = remote_port
            self.connected = False
        except Exception as e:
            exceptions.report(sys.exc_info())

class SendQueue(threading.Thread):
    def __init__(self, socket):
        try:
            threading.Thread.__init__(self)
            self.socket = socket
            self.queue = queue.Queue()
        except Exception as e:
            exceptions.report(sys.exc_info())

    def add_to_queue(self, topic, msg):
        try:
            self.queue.put((topic, msg))
        except Exception as e:
            exceptions.report(sys.exc_info())

    def run(self):
        while True:
            try:
                topic, msg = self.queue.get(True)
                self.socket.send_string("%s %s" % (topic, msg))
            except Exception as e:
                exceptions.report(sys.exc_info())

class PubSub(threading.Thread):
    def __init__(
            self,
            hostname, 
            publish_port, 
            pubsub_callback 
        ):
        try:
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
        except Exception as e:
            exceptions.report(sys.exc_info())

    def send(self, topic, msg):
        try:
            self.sendqueue.add_to_queue(topic, msg)
        except Exception as e:
            exceptions.report(sys.exc_info())

    def connect_to_publisher(self, hostname, remote_ip, remote_port):
        try:
            if hostname in self.subscriptions:
                return False
            else:
                self.subscriptions[hostname] = Subscription(hostname, remote_ip, remote_port)
                self.sub_socket.connect("tcp://%s:%s" % (remote_ip, remote_port))
                return True
        except Exception as e:
            exceptions.report(sys.exc_info())

    def subscribe_to_topic(self, topic):
        try:
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        except Exception as e:
            exceptions.report(sys.exc_info())

    def unsubscribe_from_topic(self, topic):
        try:
            topic = topic.decode('ascii') # convert to ascii range
            self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, topic)
        except Exception as e:
            exceptions.report(sys.exc_info())

    def run(self):
        while True:
            try:
                incoming_message = self.sub_socket.recv()
                topic, msg = incoming_message.split(' ', 1)
                self.pubsub_callback(topic, msg)
            except Exception as e:
                exceptions.report(sys.exc_info())


def init(
        hostname, 
        publish_port, 
        pubsub_callback,
        reporting_paramaters,
        publish_to_topic
    ):

    reports.init(
        reporting_paramaters.app_name,
        reporting_paramaters.logfile_location,
        reporting_paramaters.level,
        reporting_paramaters.print_to_stdout,
        reporting_paramaters.log_to_file,
        reporting_paramaters.publish_to_dash,
        reporting_paramaters.publish_as_topic,
        publish_to_topic,
        __file__
        )

    pubsub = PubSub(
        hostname, 
        publish_port, 
        pubsub_callback
    )
    pubsub.start()
    return pubsub
