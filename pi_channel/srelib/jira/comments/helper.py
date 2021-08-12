import logging
from urllib.error import HTTPError
from srelib.jira.comments.common import Comments
from srelib.jira.settings import JIRASettings
from srelib.jira.jira_helper import JIRAHelperBase
from srelib.jira.common import JIRAPaginationPart, JIRAHttpQueryStringRequest, JIRAOrderingPart, JIRAExpandPart

class JIRACommentsHelper(JIRAHelperBase):
    """ Use this class in order to perform operations related
    to comments in a JIRA issue.
    """
    logger = logging.getLogger(__name__)
    def __init__(self):
        JIRAHelperBase.__init__(self)

    def get_comments(
            self, 
            jira_ticket_id, 
            pagination=JIRAPaginationPart(), 
            ordering=JIRAOrderingPart(JIRAOrderingPart.ORDERING_DESCENDING_CREATED)
        ):
        """ Returns object that has information about a ticket's comments.
        Args:
            jira_ticket_id(str): The jira issue id.
            pagination(JIRAPaginationPart): Modifies request to obtain specified comments.
            ordering(JIRAOrderingPart): Contains ordering settings.  Can only be 
            initialized with JIRAOrderingPart.ORDERING_DESCENDING_CREATED or 
            JIRAOrderingPart.ORDERING_ASCENDING_CREATED
        Returns:
            Comments:  Object containing information about the comments.
            None: If comments could not be retrieved.
        """
        if(pagination is None):
            raise ValueError("pagination value can not be None")
        if(ordering is None):
            raise ValueError("ordering value can not be None")
        query_string_part = JIRAHttpQueryStringRequest()
        query_string_part.add_query_part(pagination)
        query_string_part.add_query_part(ordering)
        query_string = query_string_part.get_query_string()
        top_url = JIRASettings.get_instance().get_issue_url()
        request_url = top_url + jira_ticket_id + "/comment" + query_string
        self.logger.debug(request_url)
        json_results = self._submit_get_request(request_url)
        if(json_results is not None):
            return Comments(json_results)
        return None


def main():
    comments_helper = JIRACommentsHelper()
    comments = None
    try:
        comments = comments_helper.get_comments("CCTRL-15237")
    except HTTPError as http_error:
        code = http_error.code
        message_list = ["Unable to retrieve comments"]
        if(code == 400):
            message_list.append("Invalid value used for sort.")
        elif(code == 401):
            message_list.append("Authentication credentials are incorrect or missing")
        elif(code == 404):
            message_list.append("Issue is not found or the user does not have permission to view it")
        else:
            message_list.append("Unknown reason")
        message_list.append("Http Code: {}".format(code))
        print("; ".join(message_list))
    
    if(comments is not None):
        print("start at = {}\nTotal = {}\nMax = {}".format(
            comments.get_start_at(),
            comments.get_total(),
            comments.get_max_results()
        ))

        comment_list = comments.get_comments()
        for comment in comment_list:
            print("{}".format(comment))
    else:
        print("Unable to get comments for JIRA issue.")

if __name__ == "__main__":
    main()