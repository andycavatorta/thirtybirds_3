import netifaces
import urllib
import socket

#from thirtybirds_2_0.Logs.main import Exception_Collector

#@Exception_Collector()
class Info():
    def __init__(self):
        pass
    def get_local_ip(self):
        ifaces = netifaces.interfaces()
        for iface in ifaces:
            try:
                ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
                if ip[0:3] != "127":
                    return ip
            except Exception as e:
                pass
        return False

    def get_global_ip(self):
        try:
            return urllib.request("http://icanhazip.com").read().strip()
        except Exception as e:
            return False

    def get_host_name(self):
        try:
            return socket.gethostname()
        except Exception as e:
            return False

    def get_online_status(self):
        r = self.get_global_ip()
        return False if r==False else True

def init():
    return Info()

