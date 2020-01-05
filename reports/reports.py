"""
    The reports module provides a common system for reporting exceptions, traces, and profiles.

    Each module that imports reports passes a reference to itself so reports can get its filesystem path.
    Each module that imports reports passes a reference to network so that one instance can be used for everything.

    The reports module can print messages, log messages, and/or publishes

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback))

"""
import logging
import os
import re
import sys
import traceback

TB_ROOT_DIRECTORY = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
CONFIG = False

class Exceptions():

    def report(self, exc_info):
        if not CONFIG: # if not configured yet
            return
        parsed_exception = self.parse(exc_info)
        parsed_exception["app_name"] = CONFIG["app_name"]
        parsed_exception["level"] = CONFIG["level"]
        parsed_exception["path_to_file"] = CONFIG["path_to_file"]
        if CONFIG["print_to_stdout"]:
            print(parsed_exception)
        if CONFIG["publish_as_topic"]:
            CONFIG["publish_method"]("exception", parsed_exception)
        if CONFIG["log_to_file"]:
            logging.error("fdsaasdf")

    def parse(self, exc_info):
        exc_type, exc_value, exc_traceback = exc_info
        ex_format = traceback.format_exception(exc_type, exc_value,exc_traceback)
        exception_type, exception_message = ex_format[2].split(":",1)
        filename, line, method_and_code = ex_format[1].split(",",2)
        method, code = method_and_code.split("\n",1)
        filename = filename.split("\"",2)[1]
        line = re.sub(" line ","",line,count=1)
        method = re.sub(" in ","",method,count=1)
        path = os.path.realpath(__file__)
        return {
            "exception_path":path,
            "exception_filename":filename,
            "exception_method":method,
            "exception_line":line,
            "exception_type":exception_type,
            "exception_message":exception_message,
            "exception_code":code
        }

class Profiling():
    def __init__(self, file_ref, config):
        self.path = os.path.realpath(file_ref)
        print(config)
        print("self.path", self.path, TB_ROOT_DIRECTORY)

class Traces():
    def __init__(self, file_ref, config):
        self.path = os.path.realpath(file_ref)
        print(config)
        print("self.path", self.path, TB_ROOT_DIRECTORY)

def init(
        app_name,
        logfile_location,
        level,
        print_to_stdout,
        log_to_file,
        publish_to_dash,
        publish_as_topic,
        publish_method,
        file_ref
    ):
    if log_to_file:
        logging.basicConfig(filename=logfile_location, level=logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        error_handler = logging.StreamHandler()
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

    global CONFIG
    CONFIG = {
        "app_name":app_name,
        "logfile_location":logfile_location,
        "level":level,
        "print_to_stdout":print_to_stdout,
        "log_to_file":log_to_file,
        "publish_to_dash":publish_to_dash,
        "publish_as_topic":publish_as_topic,
        "publish_method":publish_method,
        "path_to_file": os.path.realpath(file_ref)
    }
