
import importlib
import json
from srelib.jira.common import Issue
from srelib.jira.jira_helper import JIRABase, JQLQueryRequest
from srelib.jira.jql_request import JQLRequest


class ProductionIncidentIssue(Issue):
    """ Used to represent a JIRA Production Incident ticket.
    """

    PREFIX = "PI"

    def __init__(self, json_dictionary):
        """
        Args:
            json_dictionary(dict): Has the configuration
            for the pi issue.
        """
        Issue.__init__(self, json_dictionary)

    def get_recovery_minutes(self):
        """ Returns a calculated time when a start and end time are
        supplied to the ticket.  Its the time the issue took to complete.
        Returns:
            int: The time to complete.
            None: If no recovery time is available.
        """
        return self.get_value(["fields", "customfield_39637"])


class PIHelper(JIRABase, JQLQueryRequest):

    STATE_CLOSED = 701

    def __init__(self, issue_mapper=None):
        """
        Args:
            issue_mapper(srelib.jira.issue_mapper.IssueMapper): The object used
            to map JSON issues to Issue type objects.
        """
        JIRABase.__init__(self, issue_mapper)

    def get_issue(self, pi_ticket_id):
        """  Obtain the production incident issue read-only refernce for
        the given ticket id.
        Args:
            pi_ticket_id(str): The change control issue id.
        Returns:
            ProductionIncidentIssue: The read only production incident
            object.
            None: If production incident ticket is not found.
        """
        field_list = ["assignee", "status", "creator", "created", 
            "priority", "updated", "summary","customfield_39637"]
        return super().get_issue(pi_ticket_id, field_list)


    def set_fix_type(self, pi_ticket_id, fix_type):
        """ Sets the "Fix Type" field for the given ticket.
        Args:
            pi_ticket_id(str): The PI ticket id.
            fix_type(str): One of the supported fix types.
        Returns:
            True: If able to set the ticket's fix type.
        """
        fix_type_id = None
        if(fix_type == "other"):
            fix_type_id = 18887
        else:
            self.logger.error("Unsupported fix type = {}".format(fix_type))
            return False
        update_json = {
            "fields": {
                "customfield_16228":{
                    "id":"{}".format(fix_type_id)
                }
            }
        }
        update_str = json.dumps(update_json)
        update_response = self.update_custom_field(pi_ticket_id, update_str)
        return update_response.is_success()

    def set_resolution(self, pi_ticket_id, resolution_str):
        resolution_id = None
        if(resolution_str == "complete"):
            resolution_id = 8
        else:
            self.logger.error("Unsupported resolution value = {}".format(resolution_id))
            return False
        
        update_json = {
            "fields":{
                "resolution":{
                    "id":"{}".format(resolution_id)
                }
            }
        }
        update_str = json.dumps(update_json)
        update_response = self.update_custom_field(pi_ticket_id, update_str)
        return update_response.is_success()

    def transition_to_closed(self, pi_ticket_id):
        """  Transition to closed state.  The ticket's fix type will have
        to be set prior to calling this method.
        Args:
            pi_ticket_id(str): The PI ticket id.
        Returns:
            True: If able to transition ticket to the target status.
        """
        str_transition_id = "{}".format(self.STATE_CLOSED)
        json_content = {
            "transition": {
                "id":str_transition_id
            }
        }
        return self.transition_ticket_with_json(pi_ticket_id, json_content)

    def transition_to_closed_with_fix_type(self, pi_ticket_id, fix_type):
        """  Transitions a PI ticket to the closed state with the given fix type.
        Args:
            pi_ticket_id(str): The PI ticket id.
            fix_type(str): One of the supported fix types.
        Returns:
            True: If able to transition ticket to the target status.
        """
        fix_type_id = None
        fix_type_lower = fix_type.lower()
        
        if(fix_type_lower == "other"):
            fix_type_id = 18887
        else:
            self.logger.error("Unsupported fix type = {}".format(fix_type))
            return False
        str_transition_id = "{}".format(self.STATE_CLOSED)
        json_content = {
            "transition": {
                "id":str_transition_id
            },
            "fields": {
                "customfield_16228": {
		            "id":"{}".format(fix_type_id)
                },
                "customfield_16229": {
		            "id":"{}".format(fix_company_imp)
                },
                "customfield_16230": {
		            "id":"{}".format(fix_impact_type)
                },
                "customfield_16227":[{"id":"{}".format(18878)}, {"id":"{}".format(18883)}]
            }
        }
        #print (json_content)
        return self.transition_ticket_with_json(pi_ticket_id, json_content)


def pi_query_example():
    cctrl_helper = PIHelper()
    start_date = "2020/04/15" 
    end_date = "2020/04/23"
    jql = "project = \"Production Issues\" and %28%28resolved <%3D \"{}\" and resolved >%3D \"{}\" %29%29".format(end_date, start_date)
    #jql = "project %3D \"Production Issues\" AND created >%3D \"{}\" AND created <%3D \"{}\" ORDER BY priority ASC".format(start_date, end_date)
    #jql_cctrl_month = "project = \"Change Control\" AND createdDate >= startOfMonth(-1) AND createdDate <= endOfMonth(-1)"
    
    jql_request = JQLRequest(
        jql,
        0,
        10,
        "true",
        "assignee,status,creator,created,priority,updated,summary",
        "",
        "get"
    )
    search_results = cctrl_helper.submit_search(jql_request)
    if(search_results.is_success() == False):
        print("Unable to obtain search results {}".format(search_results.get_error_message()))
        return -1
    for issue in search_results.get_issues():
        print("---")
        print("Internal JIRA id = {}".format(issue.get_issue_id()))
        print("User friendly id = {}".format(issue.get_issue_common_id()))
        user = issue.get_assignee()
        if(user is not None):
            print("Assigned to {}".format(issue.get_assignee().get_display_name()))
        else:
            print("No one is assigned this ticket")
        print("Recovery minutes = {}".format(issue.get_recovery_minutes()))
        #deploy_out = issue.get_deployout()
        #if(deploy_out is not None):
        #    deploy_result_value = deploy_out.get_deploy_out()
        #    print("Deployment result = {}".format(deploy_result_value))
        #else:
        #    print("No deployment results")
        print("---")
        

    return 0

def close_ticket_example():
    target_ticket = "PI-4915"
    pi_helper = PIHelper()
    pi_helper.transition_to_closed_with_fix_type(target_ticket, "other")

def get_issue_example():
    target_ticket = "PI-4559"
    pi_obj = PIHelper().get_issue(target_ticket)
    print(pi_obj.get_recovery_minutes())

if __name__ == "__main__":
    close_ticket_example()
    