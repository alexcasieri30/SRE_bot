from srelib.metrics.visualization import MetricGraph
import argparse
import datetime
import re
from teams_message import check_data
import requests
from brian_PI import brian_function, create, set_commands_for_PI
from helper_functions import help_msg

presets = {
    "bidding": [{"response_type": "BID", "full_name": "rtb.requests.bid"}, "Type --rtb.requests to see Bidding metric.",
                "store_true"],
    "hbase": [{"summary_type": "999_PCT", "full_name": "tsunami.hbase.read.duration"},
              "Type --tsunami.hbase.read.duration to see hbase metric.", "store_true"],
    "dma.requests": [{"full_name": "dma.requests"}, "Type --dma.requests to see this metric. ", "store_true"]
}

spec_args = [["-n", "--n", "Specify maximum number of tickets displayed.", str],
             ["-ct", "--created", "Specify start date of query. ", str]]

other_commands = [["-m", "--metric", "Specify a metric"],
                  ["-t", "--tags", "Specify tags in form 'key=value'"],
                  ["-f", "--fromtime", "Specify beginning of time interval. Default is 1d-ago. "],
                  ["-e", "--endtime", "Specify end of time interval. Default is to current. "]]


# sets the commands for grapher mode
def set_commands(list_commands):
    parser = argparse.ArgumentParser(description="Specify graph info.")
    for i in list_commands:
        parser.add_argument(i[0], i[1], help=i[2])
    parser.add_argument("-nr", "--norate", help="Uncheck 'rate_ctr' box in graph query. ", action="store_true")
    return parser


# checks time format for grapher
def check_time_format(time_string):
    num = time_string[:-5]
    if not num.isnumeric():
        return False
    if time_string[-5] not in ['h', 'd', 'm', 'w']:
        return False
    if time_string[-4:] != "-ago":
        return False
    return True


def check_regex_date(date_string):
    datetime = bool(re.match(
        '200[0-9]|201[0-9]|202[0-1][-/.](0[0-9]|1[0-2])[-/.](0[1-9]|[12][0-9]|3[01])-(0[0-9]|1[0-2]:[0-5][0-9]:[0-5][0-9])',
        date_string))
    return datetime


# checks to make sure tag values are in the correct format
def validate_tags(tag, tags_dict):
    if "=" not in tag:
        return False
    parts = tag.split("=")
    if parts[1] != "*":
        if str(parts[0]) is False or str(parts[1]) is False:
            return False
        else:
            tags_dict[parts[0]] = parts[1]
    else:
        tags_dict[parts[0]] = parts[1]
    return tags_dict


def check_valid_metric(metric_name):
    url = "http://tsdb.dc.dotomi.net/api/query?start=15m-ago&m=sum:" + metric_name
    r = requests.get(url)
    data = r.json()
    return type(data) is list


# specifically for checking that the data center tag is non-numeric
def check_dc(tags_dict):
    for i in tags_dict.items():
        if i[0] == 'dc':
            if i[1].isnumeric():
                return False
    return True


error_dict = {
    1: "Please enter valid argument. Type -h for options.",
    2: "Please enter valid maximum integer.",
    3: "Please enter a valid start date in format 'yyyy/mm/dd'.",
    4: "Ticket cannot be assigned to specified name. Check to make sure name is valid.",
    5: "Must specify information after '--PI' activation.",
    6: "Cannot use '--name', '--id', '--assign', arguments after '--all' argument.",
    7: "Cannot specify '--name' before '--assign' command. ",
    8: "Invalid ticket ID. ID must be in format: 'PROJECT-0000'.",
    9: "'--assign' command must be followed by both '--id' and '--name' commands."
}


# function for returning error messages based on codes sent through from "create" function
# between 'create' and 'brian_function' functions.
# code is a number, info is either 0 if not needed, or a name/combination of info
# returns error message or correct response string
def config_brian_errors(code, info):
    msg = None
    if code in error_dict:
        print("Error encountered.")
        return error_dict[code]
    elif code == 10:
        print("No errors encountered.")
        if "," in info:
            info = info.split(",")
            name = info[1]
            id = info[0]
            msg = f"Ticket {id} assigned to {name}."
    elif code == 11:
        print("No errors encountered.")
        msg = info
    return msg


# Removes all empty spaces from commands.
def strip_space(arg):
    stripped_word = ""
    for i in arg.split("\n"):
        word = i.replace("<div>", "").strip(";</")
        if word != "&nbsp" and len(word) > 1:
            stripped_word = word
    stripped_word = stripped_word.replace("&nbsp;", "")
    msg = stripped_word.strip().split()
    return msg


# configures commands and returns the proper payload
def parse_message(message):
    print("Argument received. Checking for errors...")
    arg = strip_space(message)
    # activates PI support mode
    if arg[0] == "--PI":
        parser = set_commands_for_PI(spec_args)
        # obj is either a code number for an error, or the req_obj
        obj, name = create(arg, parser)
        msg = config_brian_errors(obj, name)
        if msg:  # msg will be none of the object is returned
            return 1, 0, msg  # only runs when there's an error
        string = brian_function(obj)
        return 1, 0, string
    tags = {}
    times = {"fromtime": "1d-ago",
             "endtime": datetime.datetime.strftime(datetime.datetime.now(), "%Y/%m/%d-%H:%M:%S")}
    rate = True
    # validates tag, if anything is wrong, invalid = True
    for i in range(len(arg)):
        # check for norate command
        if arg[i] == "-nr" or arg[i] == "--norate":
            rate = False
        # check starttime format
        elif arg[i] == "-f" or arg[i] == "--fromtime":
            fromtime = arg[i + 1]
            if not check_regex_date(fromtime) and not check_time_format(fromtime):
                em = "Time format invalid. Correct format: 'yyyy/mm/dd-HH:MM:SS' or 'time-ago'."
                return 1, 0, em
            times['fromtime'] = fromtime
        # check endtime format
        elif arg[i] == "-e" or arg[i] == "--endtime":
            endtime = arg[i + 1]
            if not check_regex_date(endtime) and not check_time_format(endtime):
                return 1, 0, 0
            times['endtime'] = endtime
        # input tags, check for validity
        elif arg[i] == "-t" or arg[i] == "--tags":
            tag = arg[i + 1]
            tag_flag = validate_tags(tag, tags)
            if not tag_flag:
                em = "Invalid tag format. Format for tags: key=value. "
                return 1, 0, em
            else:
                tags = validate_tags(tag, tags)
                if not check_dc(tags):
                    em = "Invalid datacenter. Please enter a non-numeric datacenter."
                    return 1, 0, em
    # argument is valid
    argname = arg[0]
    if argname in presets:
        print("Preset")
        name = presets[argname][0]['full_name']
        # if argument is in the presets
        if name == "tsunami.hbase.read.duration":
            tags['dc'] = "*"
            times['fromtime'] = "6h-ago"
        url = MetricGraph.get_url_for_metric_tag(times['fromtime'], times['endtime'], name, tags, rate, True)
        print("Url: ", url)
        print("Creating graph...")
        if check_data(url) == 1:
            return 1, 0, 0
        else:
            return 2, url, 0
    else:
        print('Specify')
        try:
            # check for help command
            parser = set_commands(other_commands)
            h_m = help_msg(parser, 0)
            if arg[0] in ['-h', '--help']:
                return 1, 0, h_m
            if arg[0] not in ["-m", "--metric", "-h", "--help"]:
                em = "Error: command unrecognized."
                return 1, 0, em
            metric = arg[1]
            if not check_valid_metric(metric):
                em = "Metric invalid. Please type a valid metric. "
                return 1, 0, em
            else:
                args = parser.parse_args(arg)
                met = args.__dict__['metric']
                spec_url = MetricGraph.get_url_for_metric_tag(times['fromtime'], times['endtime'], met, tags, rate,
                                                              True)
                if check_data(spec_url) == 1:
                    em = "Invalid combination of metric and tag. "
                    return 1, 0, em
                else:
                    print("Url: ", spec_url)
                    print("Creating graph...")
                    return 2, spec_url, 0
        except:
            em = "Error: command unrecognized. Type -h for more information."
            return 1, 0, em
