import itertools
import urllib

class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""
 
    def __init__(self):
        self.form_fields = []
        self.files = []
        #TODO: should be random
        self.boundary = "Ac21BxY32"
        return
   
    def get_content_type(self):
        """
        Args:
            None
        Returns:
            str: Value for content type header.
        """
        return 'multipart/form-data; boundary=%s' % self.boundary
 
    def add_field(self, name, value):
        """Add a simple field to the form data.
        Args:
            name(str): The field name.
            value(str): The field value.
        Returns:
            None
        """
        self.form_fields.append((name, value))
        return
 
    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """ Add a file to be uploaded. 
        Args:
            fieldname(str): The filed name to use.
            filename(str): The file name.
            fileHandle(): File handle to file that will be uploaded.
            mimetype(str): The file mime type. application/octet-stream if None
            is given.
        Returns:
            None
        """
        body = fileHandle.read()
        if mimetype is None:
            mimetype = 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return
   
    def __str__(self):
        """Return a string representing the form data, including attached files.
        """
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary
       
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )
       
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )
       
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)