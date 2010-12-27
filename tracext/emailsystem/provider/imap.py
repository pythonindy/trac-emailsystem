import email
import imaplib

from trac.core import *
from trac.config import BoolOption, Option, IntOption

import tracext.emailsystem.api as api

class IMAPEmailProvider(Component):
        """ Gets emails from an IMAP inbox """
        imap_address = Option('emailsystem','imap_server',None,
                              "The imap server location")
        imap_ssl = BoolOption('emailsystem','imap_usessl',True,
                              "Whether or not to use SSL for imap connection")
        imap_port = IntOption('emailsystem','imap_port',993,
                              "Port to use when connecting via imaplib")
        imap_user = Option('emailsystem','imap_user',None,
                           "Username for imap connection")
        imap_password = Option('emailsystem','imap_password',None,
                               "Password to use when connecting")
        imap_mailbox = Option('emailsystem','imap_inbox','INBOX',
                              "Which mailbox to look in for new messages")
        
        implements(api.IEmailSystemProvider)

        def get_messages(self):
                messages = list()
                #Connect
                if self.imap_ssl:
                        server = imaplib.IMAP4_SSL(self.imap_address,self.imap_port)
                else:
                        server = imaplib.IMAP4(self.imap_address,self.imap_port)
                        
                #Login
                server.login(self.imap_user,self.imap_password)
                self.log.debug('Connected to imap')
                
                #Select Mailbox
                server.select(self.imap_mailbox)
                
                #Get Messages
                status, email_ids = server.search(None, '(UNSEEN)')
                for uid in email_ids[0].split():
                        msg = None
                        typ, msg_data = server.fetch(uid, '(RFC822)')
                        for response_part in msg_data:
                                if isinstance(response_part, tuple):
                                        msg = email.message_from_string(response_part[1])
                                        messages.append(msg)
                                        break
                
                server.logout()
                return messages
