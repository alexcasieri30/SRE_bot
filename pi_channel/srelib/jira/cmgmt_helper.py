import logging
import sys
import importlib
from srelib.jira.common import Issue
from srelib.jira.jira_helper import JIRABase, JQLQueryRequest

class ChangeManagementIssue(Issue):
    """ Used to represent a JIRA Change Management ticket.
    """

    PREFIX = "CMGMT"

    def __init__(self, json_dictionary):
        """
        Args:
            json_dictionary(dict): Has the configuration
            for the cmgmt issue.
        """
        Issue.__init__(self, json_dictionary)

class CmgmtHelper(JIRABase, JQLQueryRequest):
    """ Used to perform operations associated with Change Management tickets.
        Example of where to obtain transition ids: https://jira.cnvrmedia.net/rest/api/latest/issue/CMGMT-4087/transitions
    """
    STATE_IN_PROGRESS = 11
    STATE_IN_PROGRESS_AFTER_GATHER_REQUIREMENTS = 81
    STATE_GATHER_REQUIREMENTS = 71
    STATE_GATHER_REQUIREMENTS_AFTER_IN_PROGRESS = 91
    STATE_IMPEDED = 151
    TICKET_PREFIX = "CMGMT-"

    logger = logging.getLogger(__name__)

    def __init__(self, issue_mapper=None):
        """
        Args:
            issue_mapper(srelib.jira.issue_mapper.IssueMapper): The object used
            to map JSON issues to Issue type objects.
        """
        JIRABase.__init__(self, issue_mapper)

    def get_issue(self, cmgmt_ticket_id):
        """  Obtain the change management issue read-only refernce for
        the given ticket id.
        Args:
            cmgmt_ticket_id(str): The change management issue id.
        Returns:
            ChangeManagementIssue: The read only change management
            object.
            None: If change management ticket is not found.
        """
        field_list = ["assignee", "status", "creator", "created", 
            "priority", "updated", "summary"]
        return super().get_issue(cmgmt_ticket_id, field_list)

    def transition_to_in_progress(self, ticket_id):
        """  Transition ticket to "in progress".  This first tries to transition
        from "Todo" state to "in progress" and if that fails it tries to transition
        from "gather requirements" state to "in progress"
        Returns:
            True: If transition was successful.
            False: If the transition failed.
        """
        result = self._execute_transition(ticket_id, self.STATE_IN_PROGRESS)
        if(result == False):
            result = self._execute_transition(ticket_id, self.STATE_IN_PROGRESS_AFTER_GATHER_REQUIREMENTS)
        return result
        
    def transition_to_gather_requirements(self, ticket_id):
        """ Transition ticket to the "gather requirements" state.
        Returns:
            True: If transition was successful.
            False: If the transition failed.
        """
        result = self._execute_transition(ticket_id, self.STATE_GATHER_REQUIREMENTS)
        if(result == False):
            result = self._execute_transition(ticket_id,
                self.STATE_GATHER_REQUIREMENTS_AFTER_IN_PROGRESS
            )
        return result

    def _execute_transition(self, ticket_id, transition_id):
        if(self._check_ticket_prefix(ticket_id) == True):
            return self.transition_ticket(ticket_id, transition_id)
        else:
            self.logger.error("Invalid ticket id = {}".format(ticket_id))
        return False

    def _check_ticket_prefix(self, ticket_id):
        if(self.TICKET_PREFIX in ticket_id):
            return True
        return False



def main():
    cmgmt_helper = CmgmtHelper()
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)
    jira_status = cmgmt_helper.get_ticket_status("CMGMT-3400")
    print("The jira ticket status = {}".format(jira_status.get_status()))


if __name__ == '__main__':
    main()

