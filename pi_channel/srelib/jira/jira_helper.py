import base64
import json
import urllib.request
import os
import logging
import sys
from abc import ABCMeta, abstractmethod
from urllib.request import Request
from srelib.jira.settings import JIRASettings
from srelib.jira.jql_request import JQLRequest
from srelib.jira.common import JiraAttachementInfo, User, Status, JIRASearchResult, JIRAResponse, JiraAttachementInfo
from srelib.utils.multipart_form import MultiPartForm
from srelib.jira.issue_mapper import IssueMapper


class AttachmentResponse(JIRAResponse):
    """ Contains the results for a JSON JIRA attachement 
    request.
    """

    def __init__(self, result_id, attachment_data = None):
        """
        Args:
            result_id(int): The results id.
            attachment_data(dict):  The JSON dictionary.
        """
        JIRAResponse.__init__(self, result_id)
        self.attachment_data = attachment_data

    def get_attachment_data(self):
        """ Returns the JSON dictionary.
        """
        return self.attachment_data

class UploadAttachmentResult(JIRAResponse):
    """ Contains the results for uploading an attachment
    to a ticket.
    """
    def __init__(self, result_id, attachment_info=None):
        """
        Args:
            result_id(int): The results id.
            attachemnt_info(JiraAttachementInfo): Information for the 
            attachment after it has been uploaded
        """
        JIRAResponse.__init__(self, result_id)
        if((result_id == JIRAResponse.RESULT_SUCCESS) and (attachment_info is None)):
            raise ValueError("Must provide a non None attachment_info when operation is a success.")
        self.attachment_info = attachment_info

    def get_attachment_info(self):
        """ Returns an JiraAttachementInfo object containing information on the 
        created attachment.
        Args:
            None
        Returns:
            JiraAttachementInfo: Contains attachment info.
        """

        return self.attachment_info

class UpdateResponse(JIRAResponse):
    def __init__(self, result_id, error_message=None):
        JIRAResponse.__init__(self, result_id)
        self.set_error_message(error_message)

class JIRAHelper(object):
    """ Allows client to retrieve a singleton JIRABase object.  A 
    JIRABase object defines a few operations that can be performed
    on a JIRA ticket.
    """

    helper = None
    logger = logging.getLogger(__name__)
    
    @staticmethod
    def get_instance():
        """ Obtain a singleton JIRABase instance. 
        Returns:
            JIRABase: The singleton helper.
        """
        if (JIRAHelper.helper is None):
            JIRAHelper.helper = JIRABase()
        return JIRAHelper.helper

class JIRAHelperBase(object):
    """ Contains methods to assist in creating 
    JIRA requests.
    """

    logger = logging.getLogger(__name__)

    def __init__(self):
        pass

    def _create_expand_url(self, jira_ticket_id, expand_list, field_list):
        """ Used to add query parameters to the request url.
        Args:
            jira_ticket_id(String): The JIRA ticket id.
            expand_list(list): List of strings.  Each string is an id
            that is used to tell JIRA what fields to expand.
            field_list(list): List of strings.  The issue fields to return in 
            the json response.
        Returns:
            String: The url to use in the request.
        """
        jira_ticket_id = jira_ticket_id.upper()
        top_url = JIRASettings.get_instance().get_issue_url()
        request_url = top_url + jira_ticket_id
        has_expand_url = False
        if(expand_list is not None):
            if(len(expand_list) > 0):
                expanded_fields = ",".join(expand_list)
                request_url = request_url + "?expand=" + expanded_fields
                has_expand_url = True
        if(field_list is not None):
            if(len(field_list) > 0):
                requested_fields = ",".join(field_list)
                if(has_expand_url == True):
                    request_url = request_url + "&fields={}".format(requested_fields)
                else:
                    request_url = request_url + "?fields={}".format(requested_fields)
        return request_url
        
    def _submit_get_request(self, url):
        """ Submit an HTTP GET request to get a JSON response.
        Args:
            url(String): The request url.
        Returns:
            Dictionary: The JSON results as a dictionary.
            None: If unable to successfully make get invocation.
        """
        self.logger.debug("Making call to {}".format(url))
        q = Request(url)
        value_pass = self._get_credentials_string()
        q.add_header('Authorization', value_pass)
        q.add_header('Accept', "application/json")
        self.logger.debug("Making request to = {}".format(url))
        try:
            content = urllib.request.urlopen(q).read().decode("utf-8")
            self.logger.debug("Done making request to = {}".format(url))
            json_data = json.loads(content)
            self.logger.debug("Content from attachment {}".format(json.dumps(json_data, indent=2)))
            return json_data
        except urllib.error.HTTPError as error:
            self.logger.error("Error while retrieving attachment {}".format(error.read()))
        return None

    def _submit_delete_request(self, url):
        self.logger.debug("Making call to {}".format(url))
        q = Request(url, method="DELETE")
        value_pass = self._get_credentials_string()
        q.add_header('Authorization', value_pass)
        q.add_header('Accept', "application/json")
        self.logger.debug("Making request to = {}".format(url))
        try:
            content = urllib.request.urlopen(q).read().decode("utf-8")
            self.logger.debug("Done making request to = {}".format(url))
            return content
        except urllib.error.HTTPError as error:
            self.logger.error("{}".format(error.read()))
        return None


    def _get_credentials_string(self):
        """ Uses the API configured username and password to create
        a base64 http header BASIC authentication string.
        
        Returns:
           String: A base64 http header string for BASIC authentication.
        """
        credentials = JIRASettings.get_instance().get_credentials()
        username = credentials.get_username()
        password = credentials.get_password()
        #print("{}:{}".format(username,password))
        credentials_str = "{}:{}".format(username, password)
        credentials_str_bytes = credentials_str.encode("utf-8")
        credentials_str_b64 = base64.b64encode(credentials_str_bytes)
        value_pass = "Basic {}".format(credentials_str_b64.decode("utf-8"))
        return value_pass

class JIRABase(JIRAHelperBase):
    """ Contains operations that can be performed on 
    a JIRA ticket.

    Use the appropriate get method to obtain an attribute for the issue.  If
    more than one attribute is needed then use the "get_issue" method in order
    to retrieve multiple attributes all in one call.
    """
    logger = logging.getLogger(__name__)

    def __init__(self, issue_mapper=None):
        """
        Args:
            issue_mapper(srelib.jira.issue_mapper.IssueMapper): The object used
            to map JSON issues to Issue type objects.
        """
        JIRAHelperBase.__init__(self)
        self.issue_mapper = issue_mapper
        if(issue_mapper is None):
            self.issue_mapper = IssueMapper()

    def get_issue(self, ticket_id, field_list):
        """  Obtain the Issue object represented by the given ticket id.
        Args:
            ticket_id(str): The jira issue id.
        Returns:
            Issue: The Issue subtype for example, srelib.jira.cctrl_helper.ChangeControlIssue
            None: If jira ticket is not found.
        """
        issue_json = self._get_issue_json(ticket_id, field_list, None)
        if(issue_json is not None):
            return self.issue_mapper.get_issue(issue_json)
        return None

    def get_ticket_assignee(self, jira_ticket_id):
        """ Get the user that is assigned the ticket referenced
        by jira_ticket_id.
        Args:
            jirat_ticket_id(String): The JIRA ticket id.
        Returns:
            User: The user object that encapsulates the
            user information.
            None: If no assignee was available from ticket.
        """
        request_url = self._create_expand_url(jira_ticket_id, ["renderedFields"], ["assignee"])
        json_results = self._submit_get_request(request_url)
        if(json_results is not None):
            if("fields" in json_results):
                if("assignee" in json_results["fields"]):
                    assignee = json_results["fields"]["assignee"]
                    return User(assignee)
        return None
        
    def get_ticket_submitter(self, jira_ticket_id):
        """ Get the user that is submitted the ticket referenced
        by jira_ticket_id.
        Args:
            jira_ticket_id(String): The JIRA ticket id.
        Returns:
            User: The user object that encapsulates the
            user information.
            None: If no user available from ticket.
        """
        request_url = self._create_expand_url(jira_ticket_id, ["renderedFields"], ["creator"])
        json_results = self._submit_get_request(request_url)
        if(json_results is not None):
            if("fields" in json_results):
                if("creator" in json_results["fields"]):
                    creator = json_results["fields"]["creator"]
                    return User(creator)
        return None
        
    def get_ticket_url(self, jira_ticket_id):
        """ Returns the url that references the jira ticket.
        Args:
            jira_ticket_id(String): The JIRA ticket id.
        Returns:
            String: The URL to the JIRA ticket.
        """
        return "https://jira.cnvrmedia.net/browse/{}".format(jira_ticket_id)
        
    def get_ticket_status(self, jira_ticket_id):
        """ Returns the status value for this ticket.
        Args:
            jira_ticket_id(String): The JIRA ticket id.
        Returns:
            Status: The status object that represents ticket status.
            None: If no status available from ticket.
        """
        request_url = self._create_expand_url(jira_ticket_id, ["renderedFields"],["status"])
        json_results = self._submit_get_request(request_url)
        if(json_results is not None):
            if("fields" in json_results):
                if("status" in json_results["fields"]):
                    status = json_results["fields"]["status"]
                    return Status(status)
        return None


    def add_attachment_from_file(self, jira_ticket_id, file_name, file_path, mime_type):
        """ Add an attachment to a ticket.
        Args:
            jira_ticket_id(str): The jira ticket id.
            file_name(str): The file name as it should appear in the ticket.
            file_path(str): The local path to the file that contains the attachment content.
            mime_type(str): The file's mime type.
        Returns:
            UploadAttachmentResult: The result from uploading the attachment. 
        """
        try:
            jira_ticket_id = jira_ticket_id.upper()
            top_url = JIRASettings.get_instance().get_issue_url()
            url = top_url + jira_ticket_id + "/attachments"
            #srelib/child/attachment
            form = MultiPartForm()
            with open(file_path,'r') as f:
                form.add_file("file", file_name, f, mime_type)
            post_data = str(form)
            post_data_encoded = post_data.encode("utf-8")
            q = Request(url, data=post_data_encoded)
            value_pass = self._get_credentials_string()
            q.add_header('Authorization', value_pass)
            q.add_header('X-Atlassian-Token','nocheck')
            q.add_header('Content-type', form.get_content_type())
            q.add_header('Content-length', len(post_data_encoded))
            content = urllib.request.urlopen(q).read().decode("utf-8")
            json_data = json.loads(content)
            self.logger.debug("Return from add attachment call = {}".format(content))
            return UploadAttachmentResult(UploadAttachmentResult.RESULT_SUCCESS, JiraAttachementInfo(json_data[0]))        
        except urllib.error.HTTPError as error:
            error_message = error.read()
            if(error_message is not None):
                error_message = error_message.decode("utf-8")
            self.logger.error(error_message)
            upload_result = UploadAttachmentResult(UploadAttachmentResult.RESULT_GENERIC_REQUEST_ERROR)
            upload_result.set_http_code(error.code)
            upload_result.set_error_message(error_message)
            return upload_result


    def add_comment(self, jira_ticket_id, comment):
        """  Adds a comment to a jira ticket.
        Args:
            jira_ticket_id (string):  The JIRA ticket id.  Example "CMGMT-1234"
            comment (string): The comment to add to the ticket.
        Returns:
            Dictionary: The JIRA JSON response to the
            request.
        """
        try:
            jira_ticket_id = jira_ticket_id.upper()
            top_url = JIRASettings.get_instance().get_issue_url()
            url = top_url + jira_ticket_id + "/comment"
            
            json_content = {
                "body": comment
            }
            post_data = json.dumps(json_content)
            self.logger.debug("Update url {} with comment \"{}\"".format(url,comment))
            
            post_data_encoded = post_data.encode("utf-8")
            q = Request(url, data=post_data_encoded)
            value_pass = self._get_credentials_string()
            q.add_header('Authorization', value_pass)
            q.add_header('Accept', "application/json")
            q.add_header('Content-type', "application/json")
            q.add_header('Content-length', len(post_data_encoded))
            
            content = urllib.request.urlopen(q).read().decode("utf-8")
            self.logger.debug("Raw return valus = {}".format(content))
            json_data = json.loads(content)
            return json_data
        except urllib.error.HTTPError as error:
            self.logger.error("{}".format(error.read()))
    
    def transition_ticket(self, jira_ticket_id, transition_id):
        """ Transition the ticket to a different status.
        Args:
            jira_ticket_id (string):  The JIRA ticket id.  Example "CMGMT-1234"
            transition_id (int): The JIRA value for the status to transition.  Every
            JIRA ticket type has its own values for a state.  For example, CMGMT and CCTRL tickets 
            may not have the same value for an "in progress" state.
        Returns:
            True: If able to transition ticket to the target status.
        """
        try:
            jira_ticket_id = jira_ticket_id.upper()
            top_url = JIRASettings.get_instance().get_issue_url()
            url = top_url + jira_ticket_id + "/transitions"
            
            str_transition_id = "{}".format(transition_id)
            json_content = {
                "transition": {
                    "id": str_transition_id
                }
            }
            post_data = json.dumps(json_content)
            self.logger.debug("Update url {} with transition to  \"{}\"".format(url,str_transition_id))
            post_data_encoded = post_data.encode("utf-8")
            q = Request(url, data=post_data_encoded)
            value_pass = self._get_credentials_string()
            q.add_header('Authorization', value_pass)
            q.add_header('Accept', "application/json")
            q.add_header('Content-type', "application/json")
            q.add_header('Content-length', len(post_data_encoded))
            urllib.request.urlopen(q).read().decode("utf-8")
            return True
        except urllib.error.HTTPError as error:
            self.logger.error("{}".format(error.read()))
        return False

    def transition_ticket_with_json(self, jira_ticket_id, transition_json_dict):
        try:
            jira_ticket_id = jira_ticket_id.upper()
            top_url = JIRASettings.get_instance().get_issue_url()
            url = top_url + jira_ticket_id + "/transitions"
            post_data = json.dumps(transition_json_dict)
            self.logger.debug("Update url {} with transition json\n{}".format(url,json.dumps(transition_json_dict,indent=4)))
            post_data_encoded = post_data.encode("utf-8")
            q = Request(url, data=post_data_encoded)
            value_pass = self._get_credentials_string()
            q.add_header('Authorization', value_pass)
            q.add_header('Accept', "application/json")
            q.add_header('Content-type', "application/json")
            q.add_header('Content-length', len(post_data_encoded))
            urllib.request.urlopen(q).read().decode("utf-8")
            return True
        except urllib.error.HTTPError as error:
            self.logger.error("http code:{}, {}".format(error.code, error.read()))
        return False
    
    def get_attachment_information(self, jira_ticket_id):
        """ Retrieves a list of attachment meta data.  The meta data for each
        attachment is encapsulated in a JiraAttachmentInfo object.  Pass the
        JiraAttachmentInfo object to the get_attachment method to retrieve
        the JSON attachment.
        Args:
            jira_ticket_id(str): The jira ticket id.
        Returns:
            List(JiraAttachmentInfo): A list of JiraAttachementInfo objects
        """
        jira_ticket_id = jira_ticket_id.upper()
        request_url = JIRASettings.get_instance().get_issue_url()
        request_url = request_url + jira_ticket_id +"?expand=attachment&fields=attachment"
        json_results = self._submit_get_request(request_url)
        if(json_results is None):
            return []
        jira_attachemnts = []
        if("fields" in json_results):
            if("attachment" in json_results["fields"]):
                attachemnt_list = json_results["fields"]["attachment"]
                for attachment_dict in attachemnt_list:
                    jira_attachemnts.append(JiraAttachementInfo(attachment_dict))
        return jira_attachemnts

    def get_attachment(self, attachment_info):
        """  Get the attachment described in JiraAttachmentInfo object.
        Args:
            attachment_info(JiraAttachementInfo): Information for the attachment.
        Returns:
            AttachmentResponse: Contains attachment data or error information.
        """
        attachment_url = attachment_info.get_content_url()
        try: 
            response = self._submit_get_request(attachment_url)
            if(response is None):
                return_val = AttachmentResponse(AttachmentResponse.RESULT_GENERIC_REQUEST_ERROR)
                return_val.set_error_message("An issue was encountered when attempting to download the attachment.")
                return return_val
            else:
                return AttachmentResponse(AttachmentResponse.RESULT_SUCCESS, response)
        except Exception as e:
            self.logger.error(e)
            response = AttachmentResponse(AttachmentResponse.RESULT_GENERIC_REQUEST_ERROR)
            response.set_error_message(e)
            return response

    def delete_attachment(self, attachement_info):
        """  Delete the attachment described in JiraAttachmentInfo object.
        Args:
            attachment_info(JiraAttachementInfo): Information for the attachment.
        Returns:
            AttachmentResponse: Contains results from the delete attachment operation.
        """
        attachment_url = JIRASettings.get_instance().get_jira_api_issue_attachment_url() + attachement_info.get_id()
        try:
            response = self._submit_delete_request(attachment_url)
            if(response is None):
                return_val = AttachmentResponse(AttachmentResponse.RESULT_GENERIC_REQUEST_ERROR)
                return_val.set_error_message("An issue was encountered when attempting to delete the attachment.")
                return return_val
            else:
                return AttachmentResponse(AttachmentResponse.RESULT_SUCCESS, response)
        except Exception as e:
            response = AttachmentResponse(AttachmentResponse.RESULT_GENERIC_REQUEST_ERROR)
            response.set_error_message(e)
            return response
        
    def _get_issue_json(self, jira_ticket_id, field_list, expand_list):
        """  Get the JSON associated with an issue.
        Args:
            jira_ticket_id(str): The jira ticket id.
            field_list(list): The list of fields to return.
            expand_list(list): The list of resources to expand.  
            Some parts of a resource are not returned unless specified in the request. This simplifies responses and minimizes network traffic.
        Returns:
            Dictionary: The JSON results as a dictionary.
            None: If unable to successfully make get invocation. 
        """
        #["renderedFields"]
        request_url = self._create_expand_url(jira_ticket_id, expand_list, field_list)
        json_results = self._submit_get_request(request_url)
        return json_results
    def get_description(self, jira_ticket_id):
        """ Returns the non-html version of the description.
        Args:
            jira_ticket_id(String): The JIRA ticket id.
        Returns:
            str: The description
            None: If no description is available
        """
        request_url = self._create_expand_url(jira_ticket_id, ["renderedFields"],["description"])
        json_results = self._submit_get_request(request_url)
        if(json_results is not None):
           
            if("fields" in json_results):
                if("description" in json_results["fields"]):
                    return json_results["fields"]["description"]
        return None

    def get_html_description(self, jira_ticket_id):
        """ Returns the html version of the description.
            Args:
                jira_ticket_id(String): The JIRA ticket id.
            Returns:
                str: The description
                None: If no description is available
            """
        request_url = self._create_expand_url(jira_ticket_id, ["renderedFields"],["description"])
        json_results = self._submit_get_request(request_url)
        if(json_results is not None):    
            if("renderedFields" in json_results):
                if("description" in json_results["renderedFields"]):
                    return json_results["renderedFields"]["description"]
        return None

    def update_custom_field(self, jira_ticket_id, custom_field_json_str):
        """
        Args:
            jira_ticket_id(str): The JIRA ticket id.
            custom_field_json_str(str): The JSON that is the payload
            in the HTTP PUT.
        Returns:
            UpdateResponse: Contains information about the update operation.
        """
        #Needs to be an http put.
        top_url = JIRASettings.get_instance().get_issue_url()
        url = top_url + jira_ticket_id
        self.logger.debug("Attempting to put {} \nto url '{}'".format(custom_field_json_str, url))
        try:
            self.submit_put_request(url, custom_field_json_str)
            return UpdateResponse(UpdateResponse.RESULT_SUCCESS)
        except Exception as e:
            self.logger.exception(e)
            return UpdateResponse(UpdateResponse.RESULT_GENERIC_REQUEST_ERROR, "{}".format(e))


    def submit_post_request(self, url, post_data):
        """ Submit an HTTP POST request.
        Args:
            url(String): The request url.
            post_data(str): utf-8 encoded string. Data that is posted.
        Returns:
            str: The data returned by server.
        """
        self.logger.debug("Making POST request to = {}".format(url))
        return self.__submit_post_put(url, post_data, "POST")

    def submit_put_request(self, url, put_data):
        """ Submit an HTTP POST request.
        Args:
            url(String): The request url.
            put_data(str): utf-8 encoded string. Data used in put operation.
        Returns:
            str: The data returned by server.
        """
        self.logger.debug("Making PUT request to = {}".format(url))
        return self.__submit_post_put(url, put_data, "PUT")

    def __submit_post_put(self, url, data, http_method):
        """ Used to execute an http POST or PUT method.
        Args:
            url(str): The target url
            data(str): utf-8 encoded string
            http_method(str): Either "POST" or "PUT"
        Returns:
            str: The data returned by server.
        """
        if http_method not in ["PUT","POST"]:
            raise ValueError("method parameter must be POST or PUT")
        post_data_encoded = data.encode("utf-8")
        q = Request(url, data=post_data_encoded, method=http_method)
        q.add_header('Content-Type', 'application/json; charset=utf-8')
        q.add_header('Accept', "application/json")
        value_pass = self._get_credentials_string()
        q.add_header('Authorization', value_pass)
        q.add_header('Content-Length', len(post_data_encoded))
        
        content = urllib.request.urlopen(q).read().decode("utf-8")
        self.logger.debug("Done making request to = {},\nResult={}".format(url,content))
        return content

class JIRARequest(JIRABase):
    """ Deprecated. Used to perform JIRA queries.
    """
    def __init__(self, issue_mapper=None):
        """
        Args:
            issue_mapper(srelib.jira.issue_mapper.IssueMapper): The object used
            to map JSON issues to Issue type objects.
        """
        JIRABase.__init__(self)
        self.issue_mapper = issue_mapper
        if(issue_mapper is None):
            self.issue_mapper = IssueMapper()

    def submit_search(self, jql_request):
        """
        Returns:
            JIRASearchResult: contains the search reasults.
        """
        top_url = JIRASettings.get_instance().get_search_url()
        url = top_url + "?" + jql_request.get_query_url()
        #print(url)
        result_dict = self._submit_get_request(url)
        if(result_dict is None):
            return_val = JIRASearchResult(JIRASearchResult.RESULT_GENERIC_REQUEST_ERROR, {}, self.issue_mapper)
            return_val.set_error_message("An issue was encountered when making request to JIRA server. Please check log for details")
            return return_val
        else:
            return JIRASearchResult(JIRASearchResult.RESULT_SUCCESS, result_dict, self.issue_mapper)

class JQLQueryRequest(JIRAHelperBase):
    """ Used to perform JQL query requests.
    """

    def __init__(self, issue_mapper=None):
        """
        Args:
            issue_mapper(srelib.jira.issue_mapper.IssueMapper): The object used
            to map JSON issues to Issue type objects.
        """
        JIRAHelperBase.__init__(self)
        self.issue_mapper = issue_mapper
        if(issue_mapper is None):
            self.issue_mapper = IssueMapper()

    def submit_search(self, jql_request):
        """  Called to submit a jql query.
        Returns:
            JIRASearchResult: contains the search reasults.
        """
        top_url = JIRASettings.get_instance().get_search_url()
        url = top_url + "?" + jql_request.get_query_url()
        result_dict = self._submit_get_request(url)
        if(result_dict is None):
            return_val =  JIRASearchResult(JIRASearchResult.RESULT_GENERIC_REQUEST_ERROR, result_dict, self.issue_mapper)
            return_val.set_error_message("An issue was encountered when making request to JIRA server. Please check log for details")
            return return_val
        else:
            return JIRASearchResult(JIRASearchResult.RESULT_SUCCESS, result_dict, self.issue_mapper)


def get_attachement_example():
    helper = JIRABase()
    attachment_list = helper.get_attachment_information("CMGMT-3923")
    for attachment in attachment_list:
        print(attachment.get_size())
        print(attachment.get_mime_type())

def add_attachment_example():
    helper = JIRABase()
    ticket_id = "CMGMT-3928"
    file_name = "testing.py"
    file_path = "C:\\work\\temp\\testing.py"
    mime_type = "text/plain"
    helper.add_attachment_from_file(ticket_id, file_name, file_path, mime_type)

def add_attachment_bad_ticket_id():
    helper = JIRABase()
    ticket_id = "CMGMT-39281234441"
    file_name = "testing.py"
    file_path = "C:\\work\\temp\\testing.py"
    mime_type = "text/plain"
    upload_attachment_result = helper.add_attachment_from_file(ticket_id, file_name, file_path, mime_type)
    if(upload_attachment_result.is_success()):
        print("Attachment upload success!")
    else:
        print("Unable to upload attachment {}".format(upload_attachment_result.get_error_message()))
        print("HTTP code = {}".format(upload_attachment_result.get_http_code()))


def main():
    #add_attachment_example()
    add_attachment_bad_ticket_id()

if __name__ == '__main__':
    main()
