""" Trac email handlers having to do with tickets """

import re

from trac.core import *
from trac.config import Option
from trac.perm import PermissionSystem
from trac.ticket import Ticket
from trac.ticket.notification import TicketNotifyEmail

import tracext.emailsystem.api as api
import tracext.emailsystem.utils as utils

class ReplyToTicketEmailProcessor(Component):
    """ 
    Process emails into ticket reply comments if matching
    tickets can be found from the subject.
    """
    
    implements(api.IEmailSystemProcessor)

    def process(self, message):
        """ Reply to a ticket """
        
        self.log.debug('Processing: %(From)s to %(To)s about: %(Subject)s'%message)
        
        ticket = self.get_ticket_from_message(message)
        if not ticket:
            return False #Not consumed let other processors go
        
        user = self.get_user_from_message(message)
        
        #Get comment from email
        comment = utils.get_body_in_markup_from_message(message,remove_quoted_text=True)
        if comment:
            #Save changes to the ticket
            ticket.save_changes(user, comment)

            #Ticket notification
            tn = TicketNotifyEmail(self.env)
            tn.notify(ticket, newticket=False, modtime=ticket.time_changed)
            return True
        return False

    def get_ticket_from_message(self, message):
        """ 
        Return a ticket associated with a `message` subject
        or None if not available.
        """
        
        #Get and format the subject template
        subject_template = self.env.config.get('notification', 'ticket_subject_template')
        prefix = self.env.config.get('notification', 'smtp_subject_prefix')
        
        #Handle default prefix (trac 0.12)
        if prefix == '__default__':
            prefix = '[%s]'%self.env.project_name
        
        subject_template = subject_template.replace('$prefix', prefix).replace('$summary', 'summary').replace('$ticket.id', 'ticketid')
        subject_template_escaped = re.escape(subject_template)

        #Build the regex
        subject_re = subject_template_escaped.replace('summary', '.*').replace('ticketid', '([0-9]+)')

        #Get the real subject
        subject = utils.strip_reply_from_subject(message['subject'])
        
        #See if it matches the regex
        match = re.match(subject_re, subject)
        if not match:
            return None

        #Get the ticket
        ticket_id = int(match.groups()[0])
        try:
            ticket = Ticket(self.env, ticket_id)
        except:
            return None

        return ticket

    def get_user_from_message(self, message):
        """ Return the ticket user from `message` """
        
        user = utils.email_to_user(self.env, message['from'])
            
        #Check permissions
        perm = PermissionSystem(self.env)
        if not perm.check_permission('TICKET_APPEND', user): # None -> 'anoymous'
            raise ValueError("%s does not have TICKET_APPEND permissions" % (user or 'anonymous'))
    
        reporter = user or message['from']
        return reporter