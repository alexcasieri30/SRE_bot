from srelib.jira.pi_helper import PIHelper
from srelib.jira.jql_request import JQLRequest
from request_object import RequestJQL
import argparse
import re
from assignee import assign, check_assign_command
from helper_functions import help_msg, correct_name, convert_time
import json


# sets the commands for PI ticket parser
def set_commands_for_PI(spec_args):
    parser = argparse.ArgumentParser(description="Query and assign PI tickets.")
    for i in spec_args:
        parser.add_argument(i[0], i[1], help=i[2], type=i[3])
    parser.add_argument("--assign", "-a", help="Assign ticket to an employee.", action="store_true")
    parser.add_argument("--name", "-name", help="Username of assignee.", type=str)
    parser.add_argument("--id", "-id", help="PI Ticket ID", type=str)
    parser.add_argument("--all", "-all", help="See open PI tickets. ", action="store_true")
    return parser


# gets index of --assign command, if no --assign command then returns False
# used to help distinguish between '--name' function
def get_assign_index(command):
    for num, i in enumerate(command):
        if i in ['--assign', '-a']:
            return num
    return False


# gets the index of --name command, returns False otherwise
def get_name_index(command):
    for num, i in enumerate(command):
        if i in ['--name', '-name']:
            return num
    return False


# makes sure that if --all is specified, then no other command can be used
def handle_all(obj_dict):
    if obj_dict["all"] is True:
        for i in obj_dict.keys():
            if i != "all" and i in ['name', 'id', 'assign']:
                if obj_dict[i] not in [None, False]:
                    return False
    return True


# checks to make sure '--name' isn't specified before '--assign'.
def check_name_before_assign(args, obj_dict):
    if obj_dict['assign'] is True:
        if get_name_index(args) < get_assign_index(args):
            return False
    return True


# checks format of ticket ID
def check_valid_id(id):
    if "-" not in id:
        return False
    parts = id.split("-")
    parts[0] = parts[0].upper()
    if not parts[0].isalpha():
        return False
    if not parts[1].isnumeric():
        return False
    return True


# creates the request_object, checks for all errors
def create(args, parser):
    del args[0]
    print("Argument: ", args)
    print("Checking for errors...")
    if len(args) == 0:  # makes sure there are args after --PI
        return 5, 0
    if args[0] in ['-h', '--help']:  # sends help message
        msg = help_msg(parser, 1)
        return 11, msg
    try:
        obj_dict = parser.parse_args(args).__dict__
    except:  # invalid arguments -- checks for typo in arguments, or arguments that don't exist
        return 1, 0
    if not handle_all(obj_dict):  # '--all' command can't be followed by -name,-assign,-id
        return 6, 0
    if not check_name_before_assign(args, obj_dict):  # can't specify --name before assign
        return 7, 0
    req_obj = RequestJQL()
    # when name is before --assign, and is used for query purposes:
    if type(get_name_index(args)) is not bool:  # if --name is specified
        name = correct_name(obj_dict['name'])  # reformats name for query
        req_obj.set_assignee(name)  # add it to object
    # set_all() sets value of 'all' to either true or false depending on command
    req_obj.set_all(obj_dict['all'])
    # if assigning a ticket:
    if obj_dict['assign'] is True:
        # ensures that --assign is followed by --name and --id
        if not check_assign_command(args):  # returns boolean
            return 9, 0
        id = obj_dict['id']
        if not check_valid_id(id):  # check to see if ticket id is valid format
            return 8, 0
        name = obj_dict['name']  # used for assigning to a name
        if id is not None and name is not None:
            response = assign(id, name)
            try:
                print(response.json())
                return 4, 0
            except json.decoder.JSONDecodeError:
                print("Assignee changed.")
            comb_info = id + "," + name  # send both through, for confirmation message
            return 10, comb_info
    # for specifying max query results
    if obj_dict["n"]:
        try:
            req_obj.set_max_results(int(obj_dict['n']))
        except ValueError:  # makes sure max query results is an int
            return 2, 0
    else:
        req_obj.set_max_results(20)
    # regex for detecting date format
    if obj_dict["created"]:
        date = bool(re.match("[12]\d{3}[/](0[1-9]|1[0-2])[/](0[1-9]|[12]\d|3[01])", obj_dict['created']))
        if date:
            req_obj.set_start(obj_dict["created"])
        else:
            return 3, 0
    return req_obj, 0


# main function that takes in information and returns the output string message
def brian_function(request):
    cctrl_helper = PIHelper()
    start_date = request.get_start()
    # if name is specified, assignee will be who's tickets come up in the query
    assignee = request.get_assignee()
    max_ = request.get_max_results()
    # if name is specified, this section will be added
    # if not specified, nothing added and all open tickets will be shown
    assignee_section = f"AND assignee = \"{assignee}\"" if request.get_assignee() else ""
    # flag is for the header of the table --> 0 = specific person, 1 = all
    flag = 0
    if request.get_all():
        flag = 1  # if 1, the header needs to include assignee names
    jql = f"project = \"Production Issues\" and created > \"{start_date}\" and resolution = Unresolved {assignee_section} ORDER BY priority DESC, updated DESC"
    jql_request = JQLRequest(jql, 0, max_, "true", "assignee,status,creator,created,priority,updated,summary", "",
                             "get")
    search_results = cctrl_helper.submit_search(jql_request)
    if len(search_results.get_issues()) == 0:  # if no PI issues, return string
        if flag == 0:
            return f"No new unassigned Production Issue Tickets for \"{assignee}\"."
        return f"No open Production Issue Tickets for \"{assignee}\"."
    # begin building table
    return_string = "<table style='border-collapse:collapse;'>"
    name_header = ""
    if flag == 1:
        name_header = "<th>Name: </th>"
    return_string += f"<tr><th>Issue:</th><th>Title:</th><th>Created (UTC):</th><th>Priority:</th>{name_header}</tr> "
    for i in search_results.get_issues():
        return_string += "<tr>"
        issue_id = str(i).split("=")[1][1:]
        title = i.get_summary()
        created = convert_time(i.get_create_date())
        priority = i.get_priority().get_name()
        for j in [issue_id, title, created, priority]:
            return_string += f"<td style='padding-right: 7px; padding-left: 7px; border: solid 1px black;'>{j}</td>"
        if flag == 1:
            table_name = i.get_assignee().get_display_name()
            return_string += f"<td style='padding-right: 7px; padding-left: 7px; border: solid 1px black;'>{table_name}</td>"
        return_string += "</tr>"
    return_string += "</table>"
    print("No errors encountered.")
    return return_string
