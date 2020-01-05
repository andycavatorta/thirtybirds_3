import os
import socket
import sys

from config import settings 
from config import utils as config_utils
from reports import reports
#from system import status
from network import connection
from updates import update as thirtybirds_update
from updates import update as app_update

THIRTYBIRDS_BASE_PATH = os.path.dirname(os.path.realpath(__file__))

"""
Search bash args for override commands
"""
try:
    HOSTNAME = sys.argv[sys.argv.index("-hostname")+1]
except ValueError as e:
    HOSTNAME = socket.gethostname()
except IndexError as e:
    print("usage: python3 ____.py --hostname $hostname")
    sys.exit(0)

try:
    LOGLEVEL = sys.argv[sys.argv.index("-loglevel")+1]
except ValueError as e:
    LOGLEVEL = "ERROR"
except IndexError as e:
    print("usage: python3 ____.py --loglevel $loglevel")
    sys.exit(0)

try:
    sys.argv.index("-forceupdate")
    FORCEUPDATE = True
except ValueError as e:
    FORCEUPDATE = False

def subscribed_message_handler(topic, message):
    print(topic, message)

def network_status_message_handler(message):
    print(message)

def init(app_settings, app_base_path):
    config_utils.collate(settings, app_settings)
    # overwrite log level
    # overwrite update_on_start for both the app and for tb
    # start network
    connection_instance = connection.init(
        hostname=HOSTNAME,
        role = getattr(settings.Roles, HOSTNAME),
        pubsub_pub_port = settings.Network.pubsub_publish_port, 
        discovery_method = settings.Network.discovery_method,
        discovery_multicast_group = settings.Network.discovery_multicast_group,
        discovery_multicast_port = settings.Network.discovery_multicast_port,
        discovery_response_port = settings.Network.discovery_response_port,
        message_callback = subscribed_message_handler, 
        status_callback = network_status_message_handler, 
        heartbeat_interval = settings.Network.heartbeat_interval,
        reporting_paramaters = settings.Reporting
        )
                    
    thirtybirds_update.init(
        THIRTYBIRDS_BASE_PATH, 
        settings.Reporting, 
        settings.Update_Thirtybirds.repo_owner, 
        settings.Update_Thirtybirds.repo_name, 
        settings.Update_Thirtybirds.branch,
        connection_instance.publish_to_topic
        )

    app_update.init(
        app_base_path, 
        settings.Reporting, 
        settings.Update_App.repo_owner, 
        settings.Update_App.repo_name, 
        settings.Update_App.branch,
        connection_instance.publish_to_topic
        )
    """
    return {
        "network":connection_instance,
        "thirtybirds_update":thirtybirds_update,
        "app_update":app_update,
        }
    """
#status.init(settings.Reporting, connection_instance.publish_to_topic)


