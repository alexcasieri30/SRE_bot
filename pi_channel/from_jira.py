from srelib.jira.jql_request import JQLRequest
from srelib.jira.pi_helper import PIHelper
from processing import get_id


# gets all new PI tickets in a list
def get_new_pi_tickets():
    cctrl_helper = PIHelper()
    jql = f"project = \"Production Issues\" and resolution = unresolved ORDER BY priority DESC, updated DESC"
    jql_request = JQLRequest(jql, 0, 1000, "true", "assignee,status,creator,created,priority,updated,summary,customfield_12195", "",
                                 "get")
    search_results = cctrl_helper.submit_search(jql_request)
    return search_results.get_issues()


# formats the desired information from the PI ticket
def get_info(ticket):
    cctrl_helper = PIHelper()
    jql = "project = \"Production Issues\" and resolution = unresolved ORDER BY priority DESC, updated DESC"
    jql_request = JQLRequest(jql, 0, 1000, "true", "assignee,status,creator,created,priority,updated,summary", "",
                             "get")
    search_results = cctrl_helper.submit_search(jql_request)
    for id in search_results.get_issues():
        if get_id(str(id)) == get_id(str(ticket)):
            priority = id.get_priority().get_name()
            name = id.get_assignee().get_display_name()
            title = id.get_summary()
            return [name, id, title, priority]


# checks to see if priority change meets criteria to be posted
# if change goes to Blocker or High
def do_i_post_priority(ticket):
    priority = ticket.get_priority().get_name()
    severe_state = False
    change = False
    with open("processed_tickets.txt", "r") as f:
        lines = f.readlines()
        for i in lines:
            old_priority = i.split(",")[1]
            if old_priority in ['Blocker', 'High']:
                severe_state = True
    if not severe_state:
        if priority in ['Blocker', 'High']:
            change = True
    else:
        if priority == "Blocker":
            change = True
    return change


# checks if change meets criteria to be posted
# if impact is changed to Severe 1 or 2
def do_i_post_impact(ticket):
    new_impact = ticket.get_value(['fields', 'customfield_12195'])
    new_impact = new_impact['value'] if new_impact is not None else "None"
    # new_impact = "Severity 1"
    ticket_id = get_id(str(ticket))
    severe_state = False
    change = False
    with open("processed_tickets.txt", "r") as f:
        lines = f.readlines()
        for i in lines:
            info = i.split(",")
            if ticket_id == info[0]:
                old_impact = info[2][:-1]
                if old_impact in ['Severity 1', 'Severity 2']:
                    severe_state = True
    if severe_state:
        if new_impact == "Severity 1" and old_impact == "Severity 2":
            change = True
    else:
        if new_impact in ['Severity 1', 'Severity 2']:
            change = True
    return change


