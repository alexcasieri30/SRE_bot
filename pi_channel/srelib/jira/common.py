import importlib
import logging

class JIRAField(object):
    """ Used as a base class to specific
    JIRA fields.
    """
    def __init__(self, json_dictionary):
        """
        Args:
            json_dictionary (Dictionary):  The dictionary
            that has the information for the specific
            JIRA field.
        """
        if(json_dictionary is None):
            self.json_dictionary = {}
        else:
            self.json_dictionary = json_dictionary


    def get_json_representation(self):
        return self.json_dictionary
        
    def get_value(self, key_list):
        """ Returns the value for the key path specified
        in the key_list.  The first element in the list
        is the parent, second is the child, third grand child
        etc.  All elements in key_list must be present in the
        dictionary structures in order for a value to be returned.
        Args:
            key_list(List): A list of strings that indicate
            a key path.
        Returns:
            Object: The value of the path specified in key_list.
            None: If key isn't available.
        """
        temp_value = self.json_dictionary
        for key in key_list:
            if(key in temp_value):
                temp_value = temp_value[key]
            else:
                return None
        return temp_value

class Status(JIRAField):
    """ Represents the status value of a ticket.  The status is the workflow
    state of the ticket.
    """
   
    STATUS_NAME_PATH = ["name"]
    STATUS_ID_PATH = ["id"]

    def __init__(self, json_dictionary):
        """
        Args:
            json_dictionary(dict): Contains the status
            configuration.
        """
        JIRAField.__init__(self,json_dictionary)

    def get_status(self):
        """ Returns the string representation of the status.
        For example "Approved", "Verification", etc
        Returns:
            str: The string represenation of the status.
            None: If ticket doens't have a status.
        """
        return self.get_value(self.STATUS_NAME_PATH)

    def get_status_id(self):
        """ The JIRA int id value for this status.  Different ticket
        types will have different status ids for the same status.  For example,
        CCTRL and CMGMT tickets will have a different status id for the 
        "in progress" status.
        Returns:
            int: The id representation of the status.
            None: If ticket doesn't have an int status.
        """
        return self.get_value(self.STATUS_ID_PATH)

    def is_approved(self):
        """  Returns true if the the status is in the
        "approved" state.

        Returns:
            True: If the ticket status is "Approved"
        """
        #Using the string version of status
        return (self.get_status() == "Approved")

    def is_in_progress(self):
        """  Returns true if the the status is in the
        "in progress" state.

        Returns:
            True: If the ticket status is "Approved"
        """
        #Using the string version of status
        return (self.get_status() == "In Progress")

    def __str__(self):
        return "Status = {}, status id = {}".format(self.get_status(), self.get_status_id())

    def __repr__(self):
        return self.__str__()

class DeployApp(JIRAField):
    """ Represents a CCTRL Deployed Applicaiton.
    """
    def __init__(self, json_dictionary):
        """
        Args:
            json_dictionary(Dictionary): The dictionary
            that represents application name.
        """
        JIRAField.__init__(self, json_dictionary)
        
    def get_app_name(self):
        """ Returns the application name.
        Returns:
            str: The deployed application name.
            None: If not deployed application name available.
        """
        return self.get_value(["value"])

class DeployOut(JIRAField):
    """ Represents a CCTRL Deployed Application outcome.
    """
    def __init__(self, json_dictionary):
        """
        Args:
            json_dictionary(Dictionary): The dictionary
            that represents deployment outcome.
        """
        JIRAField.__init__(self, json_dictionary)
        
    def get_deploy_out(self):
        """ Returns the application name.
        """
        return self.get_value(["value"])

class User(JIRAField):
    """ Represents a JIRA User.
    """
    NAME_PATH = ["name"]
    EMAIL_PATH = ["emailAddress"]
    DISPLAY_NAME_PATH = ["displayName"]
    IS_ACTIVE_PATH = ["active"]
    
    def __init__(self, json_dictionary):
        """
        Args:
            json_dictionary(Dictionary): The dictionary
            that represents a JIRA user.
        """
        JIRAField.__init__(self, json_dictionary)
        
    def get_username(self):
        """ Returns the user's user name.
        Returns:
            String: Ther user's user name.
            None: If not user name is available.
        """
        return self.get_value(User.NAME_PATH)
        
    def get_email(self):
        """ Get the user's email.
        Returns:
            String: The user's email.
            None: If no email is available.
        """
        return self.get_value(User.EMAIL_PATH)
        
    def get_display_name(self):
        """  Get the user's display name.
        Returns:
            String: The way the user's username is displayed
            on a page.
            None: If no display name is available.
        """
        return self.get_value(User.DISPLAY_NAME_PATH)

    def get_is_active(self):
        """ Get the user's "is active" state.
        Returns:
            bool: True if user is active. False otherwise.
            None: If no active value is available.
        """
        return self.get_value(User.IS_ACTIVE_PATH)

    def __repr__(self):
        return "Username: {}\nDisplay Name: {}\nEmail: {}\nActive: {}".format(
            self.get_username(),
            self.get_display_name(),
            self.get_email(),
            self.get_is_active()
        )

class JiraAttachementInfo(JIRAField):
    """ Represents a JIRA attachment object.
    """

    def __init__(self, json_dictionary):
        JIRAField.__init__(self, json_dictionary)

    def get_id(self):
        """ Get the internal JIRA id for the attachment.
        Args:
            None
        Return:
            int: The attachment id.
            None: If the attachment id is not found.
        """
        return self.get_value(["id"])

    def get_filename(self):
        """  Get the attachment's file name 
        Returns:
            str: The file name.
            None: If the file name was not found on the JIRA object.
        """
        return self.get_value(["filename"])

    def get_content_url(self):
        """ Get the attachment JIRA url. 
        Returns:
            str: The url for the attachment data.
            None: If the url was not found on the JIRA object.
        """
        return self.get_value(["content"])

    def get_mime_type(self):
        """ Get the attachment's mime type.
        Returns:
            str: The mime-type of the attachment.
            None: If the mime-type was not found on the JIRA object.
        """
        return self.get_value(["mimeType"])

    def get_size(self):
        """ Get the size of the attachment in bytes.
        Returns:
            int: The number of Bytes.
        """
        return self.get_value(["size"])

    def __str__(self):
        return "{}\n{}\n{}\n{}\n{}".format(
            self.get_filename(),
            self.get_id(),
            self.get_content_url(),
            self.get_mime_type(),
            self.get_size()
        )

    def __repr__(self):
        return self.__str__()

class JIRAResponse(object):
    """ Base class for classes that are used for a 
    JIRA response.
    """
    RESULT_SUCCESS = 0
    RESULT_GENERIC_REQUEST_ERROR = -100

    def __init__(self, result_id):
        """
        Args:
            result_id(int): The id for the result.
        """
        self.result_id = result_id
        self.error_message = None
        self.http_code = None

    def set_error_message(self, error_message):
        """ Set the error message.
        Args:
            error_message(str):  The message to include
            with the result id.
        """
        self.error_message = error_message

    def get_error_message(self):
        """ Returns the error message associted with the
        result id.
        """
        return self.error_message

    def get_result_id(self):
        """
        Returns:
            int: The id for the result.
        """
        return self.result_id

    def is_success(self):
        """
        Returns:
            True: if this result is referencing a successful JIRA 
            invocation.
            False: if not a succesful JIRA invocation.
        """
        return (self.result_id == self.RESULT_SUCCESS)

    def set_http_code(self, http_code):
        """
        Args:
            http_code(str): The http code value.
        """
        self.http_code = http_code

    def get_http_code(self):
        """
        Returns:
            str: The http code
        """
        return self.http_code

class JIRASearchResult(JIRAField, JIRAResponse):
    """ Has results for a JIRA query.  JIRA uses paging for optimization purposes.
    A JIRASearchResult may not have all the issues associated with a query.
    """
    logger = logging.getLogger(__name__)
    def __init__(self, result_id, json_dictionary, issue_mapper):
        """
        Args:
            result_id(int): A JIRAResponse.RESULT_ value.
            json_dictionary(dict): The JSON returned
            by the JIRA server.
            issue_mapper(srelib.jira.issue_mapper.IssueMapper): The object used
            to map JSON issues to Issue type objects.
        """
        JIRAField.__init__(self, json_dictionary)
        JIRAResponse.__init__(self, result_id)
        self.issue_obj_list = []
        if(result_id == JIRAResponse.RESULT_SUCCESS):
            issues_list = self.get_value(["issues"])
            for issue_dict in issues_list:
                issue_obj = issue_mapper.get_issue(issue_dict)
                if(issue_obj is not None):
                    self.issue_obj_list.append(issue_obj)
                else:
                    self.logger.warning("Unable to find issue object for JSON = {}".format(issue_dict))

    def get_total_results(self):
        """ Returns the total number of issues found.  This is NOT
        the number of issues returned in the search results.

        Returns:
            int: The number of issues that were found
            when running the query.  This is NOT the number
            of issues returned in the query result.
            None: If no total is available.
        """
        return self.get_value(["total"])

    def get_start_at(self):
        """ Returns the index of the first item returned in the page. 
        Returns:
            int: The index of the first item returned in the page.
            None: If not start at value is available.
        """
        return self.get_value(["startAt"])

    def get_issues(self):
        """Returns the list of issue json dictionaries.
        Returns:
            List(Issue): A list of Issue objects.  The information
            will vary based on the query configuration.
        """
        return self.issue_obj_list

class Priority(JIRAField):
    """ Used to represent a tickets priority value.
    """
    def __init__(self, json_dictionary):
        """
        Args:
            json_dictionary(dict): The dictionary
            containing the Priority data.
        """
        JIRAField.__init__(self, json_dictionary)

    def get_name(self):
        """ Returns the string describing the priority.
        Returns:
            str: The string describing the priority.
            None: If the ticket doesn't have a string description
            for the priority.
        """
        return self.get_value(["name"])        

class Issue(JIRAField):
    """ Used to represent a JIRA issue (ticket)
    """

    def __init__(self, json_dictionary):
        JIRAField.__init__(self, json_dictionary)
        self.status = None
        self.assignee = None
        self.submitter = None
    
    def get_issue_id(self):
        """
        Returns:
            str: The internal JIRA id for this issue.
            None: If id not available. 
        """
        return self.get_value(["id"])

    def get_issue_common_id(self):
        """ Returns the shortcut project - number id.
        Returns:
            str: The common id, for example "CMGMT-1234"
            None: If id not available.
        """
        return self.get_value(["key"])

    def get_summary(self):
        """
        Returns:
            str: The summary value for the ticket.  This is basically the title.
            None: If summary not available.
        """
        return self.get_value(["fields","summary"])

    def get_status(self):
        """
        Returns:
            Status: The status representing the current workflow
            state of the ticket.
            None: If no status information is available.
        """
        return Status(self.get_value(["fields","status"]))

    def get_recovery_minutes(self):
        """ Returns a calculated time when a start and end time are
        supplied to the ticket.  Its the time it took to complete.
        Returns:
            int: The time to complete.
            None: If no recovery time is available.
        """
        return self.get_value(["fields","customfield_39637"])
    
    
    def get_assignee(self):
        """ Get the user object reprenting the user that is
        assigned the issue.
        Returns:
            User: The object representing the user.
            None: If no asignee information is available.
        """
        #print ("got here")
        user_json = self.get_value(["fields","assignee"])
        #print (user_json)
        if(user_json is not None):
            return User(user_json)
        return None

    def get_creator(self):
        """ Returns the user object reprenting the user that
        created the issue.
        Returns:
            User: The object representing the user.
            None: If no creator information is available.
        """
        user_json = self.get_value(["fields","creator"])
        if(user_json is not None):
            return User(user_json)
        return None

    def get_create_date(self):
        """ Get the create date.
        Returns:
            str: The create date.
            None: If a create day is not available.
        """
        return self.get_value(["fields","created"])
    
    def get_updated_date(self):
        """ Get the date that the issue was last updated.
        Returns:
            str: The last update date.
            None: If a create day is not available.
        """
        return self.get_value(["fields","updated"])

    def get_priority(self):
        """ Get the priority object that represents the
        issue's priority.
        Returns:
            Priority: The object representing the issue priority
            None: If a priotiy is not available.
        """
        return Priority(self.get_value(["fields","priority"]))

    def __str__(self):
        return "id = {}".format(self.get_issue_common_id())

    def __repr__(self):
        return self.__str__()

class JIRAPaginationResponse(JIRAField):
    """ Has paggination information in the response JSON.

    Info: https://developer.atlassian.com/cloud/jira/platform/rest/v3/?utm_source=%2Fcloud%2Fjira%2Fplatform%2Frest%2F&utm_medium=302#expansion
    """
    def __init__(self, response_dict):
        JIRAField.__init__(self, response_dict)

    def get_start_at(self):
        """ Returns the index of the first item returned in the page. 
        Returns:
            int: The index of the first item returned in the page. 
        """
        return self.get_value(["startAt"])

    def get_total(self):
        """ Returns the total number of items contained in all pages. 
        This number may change as the client requests the subsequent pages,
        therefore the client should always assume that the requested page can be empty. 
        Note that this property is not returned for all operations.
        Returns:
            int: The total number of items contained in all pages.
        """
        return self.get_value(["total"])

    def get_max_results(self):
        """ Returns the maximum number of items that a page can return. 
        Each operation can have a different limit for the number of items returned, 
        and these limits may change without notice. To find the maximum number of items
        that an operation could return, set maxResults to a large number—for example, 
        over 1000—and if the returned value of maxResults is less than the requested value, 
        the returned value is the maximum.
        Returns:
            int: The maximum number of items returned by the server per request.
        """
        return self.get_value(["maxResults"])


    def get_is_last(self):
        """ Indicates whether the page returned is the last one. 
        Note that this property is not returned for all operations.
        Returns:
            bool: True if its the last page. False otherwise.
            None: When property is not supported.
        """
        return self.get_value(["isLast"])

class JIRAHttpQueryPart(object):
    """ Extending classes are used to configure an http query string.
    """
    def __init__(self):
        pass

class JIRAOrderingPart(JIRAHttpQueryPart):
    """ Used to configure the ordering of the results.
    """
    ORDERING_ASCENDING_CREATED = "+created"
    ORDERING_DESCENDING_CREATED = "-created"

    def __init__(self, ordering_string):
        JIRAHttpQueryPart.__init__(self)
        if(ordering_string is None):
            raise ValueError("ordering string cant be None")
        self.ordering_string = ordering_string

    
    def get_query_string(self):
        """
        Returns:
            str: The part of the query string that configures
            the ordering of results.
        """
        return "orderBy={}".format(
            self.ordering_string
        )

class JIRAExpandPart(JIRAHttpQueryPart):
    """ Used to configure the fields that will be expanded in
    the results.
    """

    def __init__(self):
        JIRAHttpQueryPart.__init__(self)
        self.expand_values_list = []

    def add_expand_fields(self, fields_list):
        """ Add a list of fields to expand.
        Args:
            fields_list(list): A list of strings where each element
            is a field to expand.
        Returns:
            None
        """
        self.expand_values_list.extend(fields_list)

    def add_expand_field(self, field):
        """ Add a field to expand.
        Args:
            field(str): The field to expand.
        Returns:
            None
        """
        self.expand_values_list.append(field)

    def get_query_string(self):
        """
        Returns:
            str: The part of the query string that configures
            the fields included in the results.
        """
        return "expand={}".format(
            ",".join(self.expand_values_list)
        )

class JIRAPaginationPart(JIRAHttpQueryPart):
    """Used to configure the pagination values used in the
    request.
    """

    def __init__(self, start_at=0, max_results=1000):
        """
        Args:
            start_at: The page index where the results should start.
            max_results: The maximum number of hits to return in one
            response.  There may be cases where max_results will not be
            honored because it is too large.
        """
        JIRAHttpQueryPart.__init__(self)
        if(start_at is None):
            raise ValueError("start_at can not be None")
        if(max_results is None):
            raise ValueError("max_results can not be None")

        self.start_at = start_at
        self.max_results = max_results

    def get_start_at(self):
        """ Returns the index of the first item returned in the page. 
        Returns:
            int: The index of the first item returned in the page. 
        """
        return self.start_at

    def get_max_results(self):
        """ Returns the maximum number of items that a page can return. 
        Each operation can have a different limit for the number of items returned, 
        and these limits may change without notice. To find the maximum number of items
        that an operation could return, set maxResults to a large number—for example, 
        over 1000—and if the returned value of maxResults is less than the requested value, 
        the returned value is the maximum.
        Returns:
            int: The maximum number of items returned by the server per request.
        """
        return self.max_results

    def get_query_string(self):
        """
        Returns:
            str: The part of the query string that configures
            the start index and the maximum results.
        """
        return "startAt={}&maxResults={}".format(
            self.get_start_at(),
            self.get_max_results()
        )

class JIRAHttpQueryStringRequest(object):
    """ Used to aggregate JIRAHttpQueryPart object into one query string.
    """

    def __init__(self):
        self.query_parts = []

    def add_query_part(self, jira_http_query_part):
        """ Add a configuration part to the query request.
        Args:
            jira_http_query_part(JIRAHttpQueryPart): The part to add to the query.
        """
        self.query_parts.append(jira_http_query_part)

    def get_query_string(self):
        """
        Returns:
            str: The complete query string.
        """
        complete_list = []
        for part in self.query_parts:
            complete_list.append(part.get_query_string())
        
        return "?{}".format("&".join(complete_list))


