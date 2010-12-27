import re
import email
import email.Utils

#from trac.attachment import Attachment

def email_to_user(env, addr):
    """returns Trac user name from an email address"""

    name, address = email.Utils.parseaddr(addr)

    address_lower = address.lower()
    
    for uid, name, mail in env.get_known_users():
        try:
            if address_lower == mail.lower():
                return uid
        except Exception:
            return None

def reply_body(body, message):
    """ `body` appropriate to a reply `message` """
    payload = message.get_payload()
    if isinstance(payload, basestring):
        body += '\n\nOriginal message:\n %s' % payload
    return body

def get_body_in_markup_from_message(message, remove_quoted_text=False):
    """ Return the body from an email message """
    
    body = ''
    for part in message.walk():
        if part.get_content_type() == 'text/plain':
            body += part.get_payload().strip()
        #if part.get_content_type() == 'text/html':
        #body += '\n{{{\n#!html\n' + part.get_payload().strip() + '}}}'
            
    if remove_quoted_text:
        body = strip_quotes(body)
    return body

SUBJECT_RE = re.compile('( *[Rr][Ee] *:? *)*(.*)')

def strip_reply_from_subject(subject):
    """strip the REs from a Subject line"""
    match = SUBJECT_RE.match(subject)
    return match.groups()[-1]

def strip_quotes(message):
    """strip quotes from a message string"""
    body = []
    on_regex = re.compile('On .*, .* wrote:')
    for line in message.splitlines():
        line = line.strip()
        if line.strip().startswith('>'):
            continue
        if on_regex.match(line):
            continue
        body.append(line)
    body = '\n'.join(body)
    return body.strip()
