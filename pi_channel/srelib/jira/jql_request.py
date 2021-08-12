class JQLRequest(object):
    """ Used to configure a jql request.

        Documenation for query operation can be found here: https://developer.atlassian.com/server/jira/platform/rest-apis/
        And here: https://docs.atlassian.com/software/jira/docs/api/REST/6.0.8/
    """
    def __init__(self, query_string, start_at, max_results, validate_query, fields, expand, http_method="get"):
        """
        Args:
            query_string(str):  The jql query.
            start_at(int): The index of the first issue to return (0-based)
            max_results(int):  The maximum results to return.
            validate_query(str): If "true", will ask JIRA server to validate
            the query.
            fields(str): A comma separated list of fields to return.
            expand(str): A comma separated list of entities that you want expanded, identifying each of them by name.
            http_method(str): The http method to use to perform the query.  Default is an http get.
        """
        self.query_string = query_string
        self.start_at = start_at
        self.max_results = max_results
        self.validate_query = validate_query
        self.fields = fields
        self.expand = expand
        self.http_method = http_method

    def get_query_string(self):
        """
        Returns:
            str: The jql query string.
        """
        return self.query_string

    def get_start_at(self):
        """
        Returns:
            int: The index of the first issue to return (0-based)
        """
        return self.start_at

    def get_max_results(self):
        """
        Returns:
            int: The configured maximum number of issues to return.
        """
        return self.max_results

    def get_validate_query(self):
        """ Returns the validate value.
        Returns:
            str: The configured value.
        """
        return self.validate_query

    def get_fields(self):
        """  Returns the comma seperated string of field names.
        Returns:
            str: A comma seperated list.
        """
        return self.fields

    def get_expand(self):
        """  Returns the comma seperated string of fields to expand.
        Returns:
            str: A comma seperated list.
        """
        return self.expand

    def get_http_method(self):
        """ Returns the http method used to perform the query.
        Returns:
            str: The http method.
        """
        return self.http_method

    def get_query_url(self):
        """ Returns the query string that includes all the query parameters configured in
        this object.

        Returns:
            str: The query string.
        """
        query_parts = []
        query_parts.append("jql={}".format(self.query_string.replace(" ","+")))
        query_parts.append("startAt={}".format(self.start_at))
        query_parts.append("maxResults={}".format(self.max_results))
        query_parts.append("validateQuery={}".format(self.validate_query))
        query_parts.append("fields={}".format(self.fields))
        query_parts.append("expand={}".format(self.expand))
        return "&".join(query_parts)

    
        