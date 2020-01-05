import datetime
import os
import sys
import urllib.request as request

from reports import reports
exceptions = reports.Exceptions() # is there a way for a module to sniff a reference to the file that imports it?
from network import info

github = False
bash_commands = False
mojo = False
arduino = False

class Github():
    timestamp_match_tolerance = 1.0
    def __init__(self, root_path, repo_owner, repo_name, branch):
        try:
            self.root_path = root_path
            self.repo_owner = repo_owner
            self.repo_name = repo_name
            self.branch = branch
        except Exception as e:
            exceptions.report(sys.exc_info())
    def get_local_version_timestamp(self):
        try:
            return os.system("cd {} && git log -1 --format='%at'".format(self.root_path))
        except Exception as e:
            exceptions.report(sys.exc_info())

    def get_remote_version_timestamp(self):
        try:
            github_url = "https://api.github.com/repos/{}/{}/commits/{}".format(self.repo_owner, self.repo_name, self.branch)
            response = request.urlopen("https://api.github.com/repos/andycavatorta/thirtybirds_3/commits/master")
            json_data_bytes = response.read()
            json_data = str(json_data_bytes)
            # todo: the following parser is awkward and brittle. Can this be done better with regex and some exceptions?
            start = json_data.index('date":"') + 7
            end = json_data[start:].index('"') + start - 1
            datestring = json_data[start:end]
            date_string, time_string = datestring.split("T")
            hour_, minute_, seconds_ = time_string.split(":")
            year_, month_, day_ = date_string.split("-")
            return datetime.datetime.timestamp(datetime.datetime(int(year_), int(month_),  int(day_), int(hour_), int(month_), int(day_), 0))

        except Exception as e:
            exceptions.report(sys.exc_info())

    def pull(self):
        try:
            return os.system("cd {} && git pull -q --all -p".format(self.root_path))
        except Exception as e:
            exceptions.report(sys.exc_info())

    def check_if_up_to_date(self):
        try:
            network_info = info.init()
            if not network_info.get_online_status():
                return False
            local_version_timestamp = self.get_local_version_timestamp()
            remote_version_timestamp = self.get_remote_version_timestamp(self.repo_owner, self.repo_name, self.branch)
            return abs(local_version_timestamp - remote_version_timestamp) <= self.timestamp_match_tolerance
        except Exception as e:
            exceptions.report(sys.exc_info())

    def update(self):
        try:
            if self.check_if_up_to_date():
                result = self.pull()
                # todo: log all results
        except Exception as e:
            exceptions.report(sys.exc_info())

class BASH_COMMANDS():
    def __init__(self, root_path):
        try:
            self.root_path = root_path
        except Exception as e:
            exceptions.report(sys.exc_info())
        
    def get_local_version_number(self):
        try:
            pass
        except Exception as e:
            exceptions.report(sys.exc_info())
    def set_local_version_number(self):
        try:
            pass
        except Exception as e:
            exceptions.report(sys.exc_info())
    def get_unexecuted_commands(self):
        try:
            pass
        except Exception as e:
            exceptions.report(sys.exc_info())
    def update(self):
        try:
            local_version_number = self.get_local_version_number() # get local version number
            remote_version_number, versions_l = self.get_unexecuted_commands(local_version_number) # get unexecuted commands
            for command in commands_l:
                command_status = os.system(command)
                if command_status != 0:
                    pass
                    #raise something
            self.set_local_version_number(remote_version_number) # loop through commands, executing
            # update local version number
        except Exception as e:
            exceptions.report(sys.exc_info())

class Mojo():
    def __init__(self, root_path):
        try:
            self.root_path = root_path
        except Exception as e:
            exceptions.report(sys.exc_info())

class Arduino():
    pass


def report(root_path):
    pass


def update(root_path):
    github = Github(root_path)
    github.update()
    bash = BASH_COMMANDS(root_path)

def init(root_path, reporting_paramaters, repo_owner, repo_name, branch, publish_to_topic):
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

    global github
    global bash_commands
    global mojo
    global arduino

    github = Github(root_path, repo_owner, repo_name, branch)
    bash_commands = BASH_COMMANDS(root_path)
