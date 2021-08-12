
import importlib
from srelib.jira.common import Issue
from srelib.jira.jira_helper import JIRABase, JQLQueryRequest

class RootCauseAnalysisIssue(Issue):
    """ Used to represent a JIRA Root Cause Analysis ticket.
    """

    PREFIX = "RCA"

    def __init__(self, json_dictionary):
        """
        Args:
            json_dictionary(dict): Has the configuration
            for the rca issue.
        """
        Issue.__init__(self, json_dictionary)

    def get_recovery_minutes(self):
        """ Returns a calculated time when a start and end time are
        supplied to the ticket.  Its the time the issue took to complete.
        Returns:
            int: The time to complete.
            None: If no recovery time is available.
        """
        return self.get_value(["fields","customfield_39637"])


class RCAHelper(JIRABase, JQLQueryRequest):

    def __init__(self, issue_mapper=None):
        """
        Args:
            issue_mapper(srelib.jira.issue_mapper.IssueMapper): The object used
            to map JSON issues to Issue type objects.
        """
        JIRABase.__init__(self, issue_mapper)


    def get_issue(self, rca_ticket_id):
        """  Obtain the production incident issue read-only refernce for
        the given ticket id.
        Args:
            rca_ticket_id(str): The root cause analysis issue id.
        Returns:
            RootCauseAnalysisIssue: The read only root cause analysis
            object.
            None: If root cause analysis ticket is not found.
        """
        field_list = ["assignee", "status", "creator", "created", 
            "priority", "updated", "summary","customfield_39637"]
        return super().get_issue(rca_ticket_id, field_list)


if __name__ == "__main__":
    target_ticket = "RCA-285"
    issue_obj = RCAHelper().get_issue(target_ticket)
    print(issue_obj.get_recovery_minutes())