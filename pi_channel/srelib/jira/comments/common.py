import copy
from srelib.jira.common import JIRAPaginationResponse, JIRAField, User

class Comment(JIRAField):
    """ Represents a single comment. 
    """

    def __init__(self, comment_dictionary):
        """
        Args:
            comment_dictionary(dict): Contains the comment 
            data.
        """
        JIRAField.__init__(self, comment_dictionary)

    def get_text(self):
        """ Returns the text of the comment.
        Returns:
            str: The comment text.
        """
        return self.get_value(["body"])

    def get_author(self):
        """  Returns the author of the comment.
        Returns:
            User: The user object that represents the comment author.
            None: If unable to get the author.
        """
        author_info = self.get_value(["author"])
        if(author_info is not None):
            return User(author_info)
        return None

    def get_update_author(self):
        """ Returns the update auther for this comment.
        Returns:
            User: The user object that represents the comment author.
            None: If unable to get the author.
        """
        author_info = self.get_value(["updateAuthor"])
        if(author_info is not None):
            return User(author_info)
        return None

    def get_create_date(self):
        """ Returns the create date for this comment.
        Returns:
            str: The create date.  Format example 2020-03-31T19:26:47.912+0000
            None: If unable to find create date.
        """
        return self.get_value(["created"])

    def get_update_date(self):
        """ Returns the update date for this comment.
        Returns:
            str: The update date.  Format example 2020-03-31T19:26:47.912+0000
            None: If unable to find create date.
        """
        return self.get_value(["updated"])


    def __repr__(self):
        return "Author:{{\n{} }}\nCreated: {}\nComment: {}".format(
            self.get_author(),
            self.get_create_date(),
            self.get_text()
        )

class Comments(JIRAPaginationResponse):
    """ Used to hold all the comments for an issue.
    """
    def __init__(self, comments_dictionary):
        """
        Args:
            comments_dictionary(dict): The dictionary 
            containing all of the comments.
        """
        JIRAPaginationResponse.__init__(self, comments_dictionary)
        self.comments_list = []
        json_list = self.get_value(["comments"])
        for json_dict in json_list:
            self.comments_list.append(Comment(json_dict))

    def get_comments(self):
        """ Returns all the comments for a jira issue.
        Returns:
            List(Comment):  The comments associated with the ticket.
        """
        return copy.deepcopy(self.comments_list)

