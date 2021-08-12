import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SREEmail(object):

    MAX_ATTACHMENT_SIZE = 1024 * 1024 * 10

    def __init__(self):
        self.from_target = "no-reply@conversantmedia.com"
        self.attachments = []
        self.body = []
        self.is_html = False
        self.recipients = []
        self.subject = "SRE Email Message"
        self.buffer_attachment = None
        self.buffer_attachment_name = None
        self.smtp_server = 'smtp-relay.vclk.net'

    def set_from(self, from_address):
        """ Set the from address of the email.
        Args:
            from_address(str): The from address, for example no-reply@conversantmedia.com
        Returns:
            None
        """
        self.from_target = from_address
        
    def set_subject(self, subject):
        """ Set the email subject.
        Args:
            subject(str): The email subject
        Returns:
            None
        """
        self.subject = subject

    def set_buffer_attachment(self, buffer_list, buffer_attachment_name):
        """ Set a list of strings as an attachment.  Only one of these can be set per email.
        Each element in the buffer_list will be a line in the attachment document.
        Args:
            buffer_list(list):  A list of strings.
            buffer_attachment_name(str): The name that is given to the attached file.
        """
        self.buffer_attachment = buffer_list
        self.buffer_attachment_name = buffer_attachment_name
        
    def add_text_attachment(self, path):
        """ Add the path to a file that will be added as an
        attachment.
        Args:
            path(str): Local path to a file.
        Returns:
            None
        """
        self.attachments.append(path)
        
    def add_to_body(self, body_part):
        """  Apppends to body of the email. 
        Args:
            body_part(str):  Add to the email body.
        Returns:
            None
        """
        self.body.append(body_part)
        
    def set_is_html_body(self, value):
        """ If set to true the body will be treated
        as an html document.
        Args:
            value(bool): True will set the body to html. False wil reset back
            to a text body.
        Returns:
            None
        """
        self.is_html = value
        
    def send_email(self, recipients_list):
        """ Sends the email to the recipient list.
        Args:
            recipient_list(list): List of email addresses.
        """
        self.mail = smtplib.SMTP(self.smtp_server)
        # Create the container (outer) email message.
        recipient_string = ", ".join(recipients_list)
        msg = None
        has_attachments = False
        if(len(self.attachments) > 0):
            has_attachments = True
            msg = MIMEMultipart()
        elif(self.buffer_attachment is not None):
            msg = MIMEMultipart()
        else:
            #just add the body as part of the constructor
            if(self.is_html == True):
                msg = MIMEText("\n".join(self.body), "html")
            else:
                msg = MIMEText("\n".join(self.body))
            
        msg['Subject'] = self.subject
        msg['From'] = self.from_target
        msg['To'] = recipient_string

        if(self.buffer_attachment is not None):
            if(len(self.body) > 0):
                body_part = MIMEText("\n".join(self.body))
                msg.attach(body_part)
            
               
                long_string = "\n".join(self.buffer_attachment)
                byte_count = len(long_string.encode('utf-8'))
                if(byte_count > SREEmail.MAX_ATTACHMENT_SIZE):
                    print("Unable to send attachment b/c it is too large")
                    return -1
                attachment = MIMEText(long_string)
                attachment.add_header('Content-Disposition', 'attachment', filename=self.buffer_attachment_name)           
                msg.attach(attachment)
        elif(has_attachments):
            if(len(self.body) > 0):
                body_part = MIMEText("\n".join(self.body))
                msg.attach(body_part)
            
            for text_file in self.attachments:
                with open(text_file,'r') as f:
                    file_part_list = text_file.split(os.sep)
                    filename = file_part_list[-1]
                    attachment = MIMEText(f.read())
                    attachment.add_header('Content-Disposition', 'attachment', filename=filename)           
                    msg.attach(attachment)
                    
        #print(msg)
        # update to use recipients_list[] for sendmail header.  Using a string in this field will only 
        # send to one recipient even if multipel are supplied.  This is new with Python 3.7 
        self.mail.sendmail(self.from_target, recipients_list, msg.as_string())
        self.mail.quit()
                

def main():
    pass
        
if __name__ == '__main__':
    main()