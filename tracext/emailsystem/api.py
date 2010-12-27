# -*- coding: utf-8 -*-

from trac.core import *
from trac.admin import IAdminCommandProvider

class IEmailSystemProvider(Interface):
    """Fetches emails for system."""
    
    def get_messages():
        """Called during a check to get emails to process. Returns a list of email.Message objects"""

class IEmailSystemFilter(Interface):
    """Filters email"""
    
    def filter(messages):
        """Filters an email before processing. Returns None if filtered. Otherwise 
        returns modified email."""
        
class IEmailSystemProcessor(Interface):
    """Processes emails"""
    
    def process(message):
        """Called during a check to get emails to process."""


class EmailSystemManager(Component):
    """Email System manager."""

    implements(IAdminCommandProvider)
    
    providers = ExtensionPoint(IEmailSystemProvider)
    filters = ExtensionPoint(IEmailSystemFilter)
    processors = ExtensionPoint(IEmailSystemProcessor)

    # IAdminCommandProvider methods
    def get_admin_commands(self):
        yield ('emailsystem update', '<message>',
               """Notify trac that it needs to check for new emails
               
               This command should be called from a hook or chron job. It will
               trigger a fetching and then processing emails.
               """,
               self._complete_update_args, self.update)
    
    @staticmethod
    def _complete_update_args(self, args):
        return None

    # Internal Methods
    def update(self,message=None):
        """ Main update routine for the email system. 
        
        Can be passed a message to handle command line emails. """
        
        messages = list()
        if message:
            messages.append(message)
            
        self.log.info("Starting email system update")
        try: 
            self.log.info("Getting messages from providers")
            for provider in self.providers:
                    messages.extend(provider.get_messages())
        
            self.log.info('Recieved %s messages'%len(messages))
            #for msg in messages:
            #    self.log.info('%(From)s to %(To)s about: %(Subject)s'%msg)
            
            
            self.log.info("Filtering Messages")
            for scrubber in self.filters:
                messages = scrubber.filter(messages)
                
            self.log.info("Processing Messages")
            for message in messages:
                for processor in self.processors:
                    consumed = processor.process(message)
                    if consumed:
                        break
        except:
            self.log.exception('Something broke during the update')
        self.log.info("Completed email system update")
