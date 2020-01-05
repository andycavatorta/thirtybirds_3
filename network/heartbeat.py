from network import info
import threading
import time
import zmq

#from thirtybirds_2_0.Logs.main import Exception_Collector

#@Exception_Collector(["check_if_alive","record_heartbeat"])

from reports import reports
exceptions = reports.Exceptions() # is there a way for a module to sniff a reference to the file that imports it?

HEARTBEAT_SEND_PERIOD = 10
HEARTBEAT_TIMEOUT_PERIOD = 15

class Publisher():
    def __init__(self, hostname, timeout):
        try:
            self.hostname = hostname
            self.timeout = timeout
            self.last_heartbeat = time.time() - (2 * self.timeout )
        except Exception as e:
            exceptions.report(sys.exc_info())
    def check_if_alive(self):
        try:
            return True if time.time() - self.timeout < self.last_heartbeat else False
        except Exception as e:
            exceptions.report(sys.exc_info())
    def record_heartbeat(self):
        try:
            self.last_heartbeat = time.time()
        except Exception as e:
            exceptions.report(sys.exc_info())
        
#@Exception_Collector(["check_if_alive","record_heartbeat"])
class Heartbeat(threading.Thread):
    def __init__(self, hostname, pubsub, heartbeat_interval):
        try:
            threading.Thread.__init__(self)
            self.topic = "__heartbeat__"
            self.hostname = hostname
            self.pubsub = pubsub
            self.heartbeat_interval = heartbeat_interval
            self.publishers = {}
        except Exception as e:
            exceptions.report(sys.exc_info())
    def subscribe(self, hostname):
        try:
            # NOT_THREAD_SAFE
            self.publishers[hostname] = Publisher(hostname, self.heartbeat_interval)
        except Exception as e:
            exceptions.report(sys.exc_info())
    def check_if_alive(self, hostname):
        try:
            # NOT_THREAD_SAFE
            return self.publishers[hostname].check_if_alive()
        except Exception as e:
            exceptions.report(sys.exc_info())
    def record_heartbeat(self, hostname):
        try:
            # NOT_THREAD_SAFE
            if hostname not in self.publishers:
                self.subscribe(hostname)
            self.publishers[hostname].record_heartbeat()
        except Exception as e:
            exceptions.report(sys.exc_info())
    def run(self):
        while True: 
            try:
                self.pubsub.send(self.topic, self.hostname)
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                exceptions.report(sys.exc_info())

def init(hostname, pubsub, reporting_paramaters, publish_to_topic, heartbeat_interval):
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
    hb = Heartbeat(hostname, pubsub, heartbeat_interval)
    hb.start()
    return hb


