from srelib.utils.credentials import CredentialManager, JSONCredentialStrategy
from srelib.utils.sre_lib_settings import SRELibSettings
#from srelib.jira.pyt_credentials import PYTCredentialStrategy

class JIRASettings(object):
    """ Used to obtain settings to be used with
    the jira API.
    """
    settings = None
    JIRA_API_URL = 'https://jira.cnvrmedia.net/rest/api/latest/'
    JIRA_API_URL_ATTACHMENT = JIRA_API_URL + "attachment/"
    
    def __init__(self, credential_manager=None):
        """
        Args:
            credential_manager(CredentialManager):  Must have
            an entry for the "jira" credentials.
        """
        self.credentials_manager = credential_manager
        if(credential_manager is None):
            srelib_settings = SRELibSettings.get_instance()
            json_file_location = srelib_settings.get_config_location() + "srelib_credentials.json"
            credential_strategy = JSONCredentialStrategy(json_file_location)
            #use of pyc
            #credential_strategy = PYTCredentialStrategy()
            self.credentials_manager = CredentialManager(credential_strategy)

        self.credentials = self.credentials_manager.get_credentials("jira")
    
    @staticmethod
    def get_instance():
        if(JIRASettings.settings is None):
            JIRASettings.settings = JIRASettings()
        return JIRASettings.settings
        
    def get_credentials(self):
        """Obtain a JIRACredentials object that contains credential
        information.
        
        Returns:
            srelib.utils.credentials.Credentials: contains credential information.
        """
        return self.credentials
        
    def get_issue_url(self):
        """ Returns the base url for a jira issue.
        
        Returns:
            A string url that targets the issue endpoint of the 
            jira api.
        """
        return 'https://jira.cnvrmedia.net/rest/api/latest/issue/'

    def get_search_url(self):
        """ Returns the JIRA target url for peforming a search.
        Returns:
            str: The endpoint url used to perform a search.
        """
        return 'https://jira.cnvrmedia.net/rest/api/latest/search/'

    def get_jira_api_issue_attachment_url(self):
        """ Returns the JIRA REST API target url for peforming an attachment operation
        Returns:
            str: The endpoint url used to perform an attachment operation.
        """
        return self.JIRA_API_URL_ATTACHMENT 
        