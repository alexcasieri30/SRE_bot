import importlib

class IssueMapper(object):
    """ Used to map a JSON issue dictionary to an object that extends srelib.jira.common.Issue 
    """

    def __init__(self):
        self.mapping = {}
        self.register_issue_type("CCTRL","srelib.jira.cctrl_helper.ChangeControlIssue")
        self.register_issue_type("CMGMT","srelib.jira.cmgmt_helper.ChangeManagementIssue")
        self.register_issue_type("RCA","srelib.jira.rca_helper.RootCauseAnalysisIssue")
        self.register_issue_type("PI","srelib.jira.pi_helper.ProductionIncidentIssue")
        self.register_issue_type("MPUB","srelib.jira.common.Issue")
        self.register_issue_type("CPEUI","srelib.jira.common.Issue")

    def get_issue(self, issue_json):
        """ Returns the appropriate Issue object.
        Args:
            issue_json(dict): The Issue's JSON dictionary.
        Returns:
            Issue: An object that extends the Issue class.
        """
        if("key") in issue_json:
            key_val = issue_json["key"]
            issue_id_list = key_val.split("-")
            prefix = issue_id_list[0]
            if(prefix in self.mapping):
                return self.mapping[prefix](issue_json)    
        return None

    def register_issue_type(self, issue_prefix, issue_class_full_name):
        """ Register a prefix to class mapping.
        Args:
            issue_prefix(str): The ticket prefix, for example "PI", "CCTRL", etc...
            issue_class_full_name(str): The full name of the Issue class that should be
            used for issues with the given prefix.  A full name example is "srelib.jira.pi_helper.ProductionIncidentIssue"
        Returns:
            Issue:  A class that extends the Issue class.
        """
        fullname_tokens = issue_class_full_name.split('.')
        end_index = len(fullname_tokens) - 1
        module_list = fullname_tokens[0:end_index]
        module_name = ".".join(module_list)
        class_name = fullname_tokens[-1]
        module = importlib.import_module(module_name)
        issue_class_pointer = getattr(module, class_name)
        self.mapping[issue_prefix] = issue_class_pointer

if __name__ == "__main__":
    im = IssueMapper()
    im.register_issue_type("RCA", "srelib.jira.rca_helper.RootCauseAnalysisIssue")

