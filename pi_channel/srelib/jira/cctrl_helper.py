import logging
import importlib
import json
from srelib.jira.jira_helper import JIRABase, JQLQueryRequest
from srelib.jira.settings import JIRASettings
from srelib.jira.common import Issue, DeployOut, DeployApp, JIRASearchResult
from srelib.jira.jql_request import JQLRequest

class ChangeControlIssue(Issue):
    """ Used to represent a JIRA Change Control ticket.
    """

    PREFIX = "CCTRL"

    def __init__(self, json_dictionary):
        """
        Args:
            json_dictionary(dict): The JSON dictionary that
            contains the issue information.
        """
        Issue.__init__(self, json_dictionary)

    def get_deployout(self):
        """ Returns the deployment status for the issue.
        Returns:
            DeployOut: The deployment status object.
            None: If no deployement status is available.
        """
        json_dict = self.get_value(["fields","customfield_13624"])
        if(json_dict is not None):
            return DeployOut(json_dict)
        return None
    
    def get_application(self):
        """ Returns a DeployApp object that contains information for application that was deployed.
        Returns:
            DeployApp: Information for the deployed application.
            None: If no deployment information is available.
        """
        json_dict = self.get_value(["fields","customfield_13051"])
        if(json_dict is not None):
            return DeployApp(json_dict)
        return None

    def get_cctrl_date_time(self):
        """ Returns the date & time for the cctrl.
        """
        return self.get_value(["fields","customfield_13728"])

class CctrlHelper(JIRABase, JQLQueryRequest):
    """ Used to perform operations associated with change control (CCTRL) tickets.
    """
    #CCTRL state ids used with transition the tic
    STATE_IN_PROGRESS = 41
    STATE_PENDING_APPROVAL = 191
    STATE_PASS = 111
    STATE_FAIL = 131
    #the ticket prefix
    TICKET_PREFIX = "CCTRL-"

    def get_description(self, cctrl_ticket_id):
        return super().get_description(cctrl_ticket_id)
    
    def get_html_description(self, cctrl_ticket_id):
        return super().get_html_description(cctrl_ticket_id)
    logger = logging.getLogger(__name__)

    def __init__(self, issue_mapper=None):
        """
        Args:
            issue_mapper(srelib.jira.issue_mapper.IssueMapper): The object used
            to map JSON issues to Issue type objects.
        """
        JIRABase.__init__(self, issue_mapper)


    def get_issue(self, cctrl_ticket_id):
        """  Obtain the change control issue read-only refernce for
        the given ticket id.
        Args:
            cctrl_ticket_id(str): The change control issue id.
        Returns:
            ChangeControlIssue: The read only change control
            object.
            None: If change control ticket is not found.
        """
        field_list = ["assignee", "status", "creator", "created", 
            "priority", "updated", "summary", "customfield_13051", 
            "customfield_13624"]
        return super().get_issue(cctrl_ticket_id, field_list)


    def transition_to_in_progress(self, cctrl_ticket_id):
        """  Transition ticket to "in progress".
        Args:
            cctrl_ticket_id(str): The change control ticket id.
        Returns:
            True: If transition was successful.
            False: If the transition failed.
        """
        if(self._check_ticket_prefix(cctrl_ticket_id) == True):
            return self.transition_ticket(cctrl_ticket_id, self.STATE_IN_PROGRESS)
        else:
            self.logger.error("Invalid cctrl ticket id given {}".format(cctrl_ticket_id))
        return False

    def set_deployed_by(self, cctrl_ticket_id, user_name):
        """
        Args:
            cctrl_ticket_id(str): The change control id.
            user_name(str): The user name to set for the deployed by field.
        Returns:
            bool: True if it was set, False otherwise.
        """
        if(self._check_ticket_prefix(cctrl_ticket_id) == True):
            update_json = {
                "fields":{
                    "customfield_11628":{
                        "name":"{}".format(user_name)
                    }
                }
            }
            update_str = json.dumps(update_json)
            update_response = self.update_custom_field(cctrl_ticket_id, update_str)
            return update_response.is_success()
        else:
            self.logger.error("Invalid cctrl ticket id given {}".format(cctrl_ticket_id))
        return False

    def _check_ticket_prefix(self, cctrl_ticket_id):
        if(self.TICKET_PREFIX in cctrl_ticket_id):
            return True
        return False

def attachment_example():
    helper = JIRABase()
    attachment_list = helper.get_attachment_information("CMGMT-3923")
    for attachment in attachment_list:
        print(attachment.get_size())
        print(attachment.get_mime_type())

def paging_example():
    cctrl_helper = CctrlHelper()
    #Will be set to True after all issues are obtained.
    all_results_retrieved = False
    #The first index of the first issue to be returned.
    start_index = 0
    #The maximum number of issues to return.
    max_returned = 50
    #The total number of issues retrieved.
    total_issues_retrived = 0
    #The total number of results for the query.
    total_results_for_query = None
    #The query.
    jql_cctrl_month = "project = \"Change Control\" AND createdDate >= startOfMonth(-1) AND createdDate <= endOfMonth(-1)"
    #keeps track of the number of times the query was executed.
    query_count = 1
    while(all_results_retrieved == False):
        print("Query count = {}".format(query_count))
        query_count += 1
        jql_request = JQLRequest(
            jql_cctrl_month,
            start_index,
            max_returned,
            "true",
            "assignee,status,creator,created,priority,updated,summary,customfield_13051,customfield_13624",
            #"",
            "",
            "get"
        )
        #execute query  
        search_results = cctrl_helper.submit_search(jql_request)
        if(search_results.is_success() == False):
            print("Unable to obtain search results {}".format(search_results.get_error_message()))
            return -1
        total_results_for_query = search_results.get_total_results()
        issues_list = search_results.get_issues()
        issues_returned = len(issues_list)
        total_issues_retrived += issues_returned
        start_index += issues_returned
        print("Total results for query = {}".format(total_results_for_query))
        print("Total returned = {}".format(issues_returned))
        print("Returned batch starts at index = {}".format(search_results.get_start_at()))
        if(total_issues_retrived >= total_results_for_query):
            all_results_retrieved = True
    print("Total issues retrieved = {}".format(total_issues_retrived))
    
def get_status_example():
    target_ticket = "CCTRL-16079"
    target_ticket = "CMGMT-4058"
    target_ticket = "RCA-259"
    target_ticket = "PI-4561"
    #create the object that is used to get a refernce to the ChangeControlIssue object
    use_ticket_obj = False
    status_obj = None
    cctrl_helper = CctrlHelper()
    if(use_ticket_obj == False): 
        status_obj = cctrl_helper.get_ticket_status(target_ticket)
    else:
        status_obj = cctrl_helper.get_issue(target_ticket).get_status()
    status_str = status_obj.get_status()
    print("The ticket {} is in state (status) = {}, id {}".format(target_ticket, status_str, status_obj.get_status_id()))
    if(status_obj.is_in_progress() ==  True):
        print("The ticket is in progress")
    else:
        print("Ticket is not in progreess, it is in the {} state".format(status_str))

def get_description_example():
    target_ticket = "CCTRL-16887"
    helper = CctrlHelper()
    print("non-html description = {}".format(helper.get_description(target_ticket)))
    print("\n\nhtml version of the description = {}".format(helper.get_html_description(target_ticket)))
    

def set_deployed_by_example():
    cctrl_helper = CctrlHelper()
    #anoronha
    is_ok = cctrl_helper.set_deployed_by("CCTRL-18047","anoronha")
    if(is_ok == True):
        print("Update was a success.")
    else:
        print("Was not able to update.")

if __name__ == '__main__':
    set_deployed_by_example()
