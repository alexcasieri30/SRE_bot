import json
import logging
import base64
import importlib

#
# Various strategies for credential obfuscation:
# https://stackoverflow.com/questions/157938/hiding-a-password-in-a-python-script-insecure-obfuscation-only
#

class CredentialStrategy(object):
    """ Interface for credential strategy implementations.
    """

    def get_credential_identifiers(self):
        """  Every username and password is identified by and id.  This returns a list
        of ids found in this strategy.
        Returns:
            list(str): A list of ids used to identify the use of the username-password.
        """
        pass

    def get_credentials(self, credential_identifier):
        """ Returns a Credentials object for the given credential identifier.
        Args:
            credential_identifier(str): The identifier for the requested credentials
        Returns:
            Credentials: Has username and password information.
            None: If no credential information found.
        """
        pass


class JSONCredentialStrategy(CredentialStrategy):
    """ A credential strategy that reads configuration via
    a JSON file.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, json_file_location):
        """
        Args:
            json_file_location(str): The path to the credentials JSON file.
        """
        self.id_to_credentials = {}
        self.register_credentials(json_file_location)

    def register_credentials(self, json_file_location):
        """ Register the credential information in a JSON file.
        Args:
            json_file_location(str): The path to the credentials JSON file.
        """
        with open(json_file_location, 'r') as fp:
            json_data = json.load(fp)
            if("credentials" in json_data):
                credential_list = json_data["credentials"]
                for credentials in credential_list:
                    cred_id = credentials["id"]
                    username = credentials["u"]
                    password = credentials["p"]
                    repr = base64.b64decode(bytes(username,'utf-8'))
                    username = repr.decode('utf-8')
                    repr = base64.b64decode(bytes(password, 'utf-8'))
                    password = repr.decode('utf-8')
                    cred = Credentials(username, password)
                    self.id_to_credentials[cred_id] = cred

    def get_credential_identifiers(self):
        """  Every username and password is identified by and id.  This returns a list
        of ids found in this strategy.
        Returns:
            list(str): A list of ids used to identify the use of the username-password.
        """
        return list(self.id_to_credentials.keys())

    def get_credentials(self, credential_identifier):
        """ Returns a Credentials object for the given credential identifier.
        Args:
            credential_identifier(str): The identifier for the requested credentials
        Returns:
            Credentials: Has username and password information.
            None: If no credential information found.
        """
        if(credential_identifier in self.id_to_credentials):
            return self.id_to_credentials[credential_identifier]
        return None

class CredentialManager(object):
    """ Used to manage multiple credential strategies.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, credential_strategy):
        """
        Args:
            credential_strategy(CredentialStrategy): The credential strategy.
        """
        self.id_to_credentials = {}
        self.credential_strategies = []
        self.add_credential_strategy(credential_strategy)

    def add_credential_strategy(self, credential_strategy):
        """  Add a credential strategy to be managed.
        Args:
            credential_strategy(CredentialStrategy): The credential strategy.
        Returns:
            None
        """
        self.credential_strategies.append(credential_strategy)
        credential_ids_list = credential_strategy.get_credential_identifiers()
        for credential_id in credential_ids_list:
            credentials = credential_strategy.get_credentials(credential_id)
            if(credential_id in self.id_to_credentials):
                self.logger.warning("Replacing credentials for id {}".format(credential_id))
            self.id_to_credentials[credential_id] = credentials

    def get_credentials(self, credential_identifier):
        """ Get the credential information for the given identifier.
        Args:
            credential_identifier(str): The identifier that points to the requested
            credentials.
        Returns:
            Credentials: Contains username and password.
        """
        if(credential_identifier in self.id_to_credentials):
            return self.id_to_credentials[credential_identifier]
        return None

class Credentials(object):
    """ Holds username and password.
    """

    def __init__(self, username, password):
        """
        Args:
            username(str): The user name.
            password(str): The password.
        """
        self.username = username
        self.password = password

    def get_password(self):
        """ Returns the password.
        Returns:
            str: The password.
        """
        return self.password

    def get_username(self):
        """ Returns the user name.
        Returns:
            str: The user name.
        """
        return self.username


