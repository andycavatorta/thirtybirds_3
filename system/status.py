"""A one line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  foo = ClassFoo()
  bar = foo.FunctionBar()
"""

import platform

from reports import reports
from config import settings as reports_config
exceptions = reports.Exceptions() # is there a way for a module to sniff a reference to the file that imports it?

platform_name = ""

def get_temp():
    try:
        if platform_name == "Raspbian":
            return commands.getstatusoutput("/opt/vc/bin/vcgencmd measure_temp")[1]
        if platform_name == "Ubuntu":
            return None
        if platform_name == "Darwin":
            return None
    except Exception as e:
        exceptions.report(sys.exc_info())

def get_update_script_version():
    try:
        if platform_name == "Raspbian":
            pass
        if platform_name == "Ubuntu":
            return None
        if platform_name == "Darwin":
            return None
    except Exception as e:
        exceptions.report(sys.exc_info())

    (updates, ghStatus, bsStatus) = updates_init("/home/pi/oratio", False, False)
    return updates.read_version_pickle()

def get_git_timestamp():
    try:
        if platform_name == "Raspbian":

        if platform_name == "Ubuntu":
            return None
        if platform_name == "Darwin":
            return None
    except Exception as e:
        exceptions.report(sys.exc_info())

    return commands.getstatusoutput("cd /home/pi/oratio/; git log -1 --format=%cd")[1]

def get_cpu():
    try:
        if platform_name == "Raspbian":

        if platform_name == "Ubuntu":
            return None
        if platform_name == "Darwin":
            return None
    except Exception as e:
        exceptions.report(sys.exc_info())

    bash_output = commands.getstatusoutput("uptime")[1]
    split_output = bash_output.split(" ")
    return split_output[12]

def get_uptime():
    try:
        if platform_name == "Raspbian":

        if platform_name == "Ubuntu":
            return None
        if platform_name == "Darwin":
            return None
    except Exception as e:
        exceptions.report(sys.exc_info())

    bash_output = commands.getstatusoutput("uptime")[1]
    split_output = bash_output.split(" ")
    return split_output[4]

def get_disk():
    try:
        if platform_name == "Raspbian":
            
        if platform_name == "Ubuntu":
            return None
        if platform_name == "Darwin":
            return None
    except Exception as e:
        exceptions.report(sys.exc_info())
    # stub for now
    return "0"

def update():
    try:
        pass
    except Exception as e:
        exceptions.report(sys.exc_info())

def shutdown():
    try:
        pass
    except Exception as e:
        exceptions.report(sys.exc_info())

def reboot():
    try:
        pass
    except Exception as e:
        exceptions.report(sys.exc_info())

def init(reporting_paramaters, publish_to_topic):
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
    global platform_name
    platform_names = ["Ubuntu", "Darwin", "Raspbian"]
    platform_name_raw = platform.version()
    for _platform_name_ in platform_names:
        if _platform_name_ in platform_name_raw:
            platform_name = _platform_name_
            return
