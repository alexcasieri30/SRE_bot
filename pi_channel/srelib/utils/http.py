import logging
import urllib.request
from urllib.request import Request

class HTTPCommands(object):

    logger = logging.getLogger(__name__)

    @staticmethod
    def submit_get_request(url):
        HTTPCommands.logger.debug("Making GET request to = {}".format(url))
        q = Request(url, method="GET")
        q.add_header('Accept', "*/*")
        HTTPCommands.logger.debug("Making GET request to = {}".format(url))
        content = urllib.request.urlopen(q).read().decode("utf-8")
        HTTPCommands.logger.debug("Done making GET request to = {},\nResult={}".format(url,content))
        return content

    @staticmethod
    def submit_post_request(url, post_data):
        """ Submit an HTTP POST request.
        Args:
            url(String): The request url.
            post_data(str): utf-8 encoded string. Data that is posted.
        Returns:
            str: The data returned by server.
        """
        HTTPCommands.logger.debug("Making POST request to = {}".format(url))
        return HTTPCommands.__submit_post_put(url, post_data, "POST")

    @staticmethod
    def submit_delete_request(url):
        """ Submit an HTTP DELETE request.
        Args:
            url(String): The request url.
        Returns:
            str: The data returned by server.
        """
        q = Request(url, method="DELETE")
        q.add_header('Accept', "*/*")
        HTTPCommands.logger.debug("Making DELETE request to = {}".format(url))
        content = urllib.request.urlopen(q).read().decode("utf-8")
        HTTPCommands.logger.debug("Done making request to = {},\nResult={}".format(url,content))
        return content

    @staticmethod
    def submit_put_request(url, put_data):
        """ Submit an HTTP POST request.
        Args:
            url(String): The request url.
            put_data(str): utf-8 encoded string. Data used in put operation.
        Returns:
            str: The data returned by server.
        """
        HTTPCommands.logger.debug("Making PUT request to = {}".format(url))
        return HTTPCommands.__submit_post_put(url, put_data, "PUT")

    @staticmethod
    def __submit_post_put(url, data, http_method):
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
        q = Request(url, data=data, method=http_method)
        q.add_header('Content-Type', 'application/json; charset=utf-8')
        q.add_header('Content-Length', len(data))
        
        content = urllib.request.urlopen(q).read().decode("utf-8")
        HTTPCommands.logger.debug("Done making request to = {},\nResult={}".format(url,content))
        return content
