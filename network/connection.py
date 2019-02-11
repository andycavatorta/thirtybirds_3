"""
This module contains robust functions for creating and maintianing a persistent network connection between two different network stacks.

It manages network discovery, socket connections, pubsub behaviors, detection of disconnection, reconnection, and status messaging.

The syntax for invoking this module is:

my_connection = network.connection(
        hostname, # the hostname of this computer
        role, # [ "client"|"server" ]
        pubsub_pub_port, # port for pubsub connection
        discovery_method, # [network.DISCOVERY_METHOD_BROKER|network.DISCOVERY_METHOD_MULTICAST|network.DISCOVERY_METHOD_STATIC]
        discovery_parameters, # for broker or static: ("address":"","port":0), for multicast: ("address":"","port":0,"response_port":0)
        message_callback, # callback function to receive incoming messages
        status_callback, # callback function to receive connection status messages
        heartbeat_interval# seconds between heartbeats ( optional )
    )

"""
#########################################
######## IMPORTS, PATHS, GLOBALS ########
#########################################

import threading
import time

import discovery # manages network discovery
import heartbeat # manages the detection of disconnection
import network
import pubsub # manages pubsub behaviors

class Connection(threading.Thread):
    def __init__(
            self, 
            hostname,
            role,
            pubsub_pub_port, 
            discovery_method,
            discovery_parameters,
            message_callback, 
            status_callback, 
            heartbeat_interval = 15
        ):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.role = role
        self.pubsub_pub_port = pubsub_pub_port
        self.discovery_method = discovery_method
        self.discovery_parameters = discovery_parameters
        self.message_callback = message_callback
        self.status_callback = status_callback
        self.heartbeat_interval = heartbeat_interval
        self.publishers = {} # for use with heartbeat testing
        self.discovery = discovery.init(
            hostname,
            network.DISCOVERY_ROLE_CALLER if role == network.CONNECTION_ROLE_CLIENT else network.DISCOVERY_ROLE_RESPONDER, # Any process can be a network caller or responder.  Here we map it to client/server roles. 
            discovery_method,
            discovery_parameters,
            self.local_discovery_status_callback,
            heartbeat_interval
            )
        self.pubsub = pubsub.init(
            hostname,
            pubsub_pub_port, 
            self.pubsub_callback
            )
        self.heartbeat = heartbeat.init(
            hostname,
            self.pubsub
            )
    def local_discovery_status_callback(self,message): # called when remote connection is discovered
        time.sleep(0.1) # what's this race condition about?
        #if hasattr(self, "heartbeat"): # under what circumstances would self not have a 'heartbeat' attribute?
        if message["status"] == network.DISCOVERY_STATUS_FOUND: # if device is discovered
            self.heartbeat.subscribe(message["hostname"]) # ignored if redundant
            if self.pubsub.connect_to_publisher(message["hostname"], message["ip"], self.pubsub_pub_port): # this will be ignored if already connected
                self.pubsub.subscribe_to_topic("__heartbeat__") # subscribe to heartbeats from remote connection
                self.publishers[message["hostname"]] = {"connected":False} # connected is not redundant here.  we use its state to detect changes to heartbeat status
        self.status_callback(message)

    def pubsub_callback(self, message, host):
        if message == "__heartbeat__":
            self.heartbeat.record_heartbeat(host)
        else:
            self.message_callback((message, host))

    def subscribe_to_topic(self, topic): # scoped upward for convenience
        self.pubsub.subscribe_to_topic(topic)

    def publish_to_topic(self, topic, message): # scoped upward for convenience
        self.pubsub.send(topic, message)

    def run(self):
        while True:
            for publisher_hostname,val in self.publishers.items():# loop through all known publishers, check live status
                alive = self.heartbeat.check_if_alive(publisher_hostname)
                print "Network.Manager.run", publisher_hostname, alive
                if self.publishers[publisher_hostname]["connected"] != alive: # detect a change is heartbeat status
                    self.publishers[publisher_hostname]["connected"] = alive
                    if alive == False and self.role == network.CONNECTION_ROLE_CLIENT: # if a publisher has just come back online.
                        self.discovery.begin()
            time.sleep(10)
    
def init(
        hostname, # the hostname of this computer
        role, # [ "client"|"server" ]
        pubsub_pub_port, # port for pubsub connection
        discovery_method, # ["static"|"multicast"|"broker"]
        discovery_parameters, # for broker or static: ("address":"","port":0), for multicast: ("address":"","port":0,"response_port":0)
        message_callback, # callback function to receive incoming messages
        status_callback, # callback function to receive connection status messages
        heartbeat_interval = 15 # seconds between heartbeats ( optional )
    ):
    connection = Connection(
        hostname, # the hostname of this computer
        role,
        pubsub_pub_port, 
        discovery_method,
        discovery_parameters,
        message_callback, 
        status_callback, 
        heartbeat_interval
    )
    connection.start()
    return connection

