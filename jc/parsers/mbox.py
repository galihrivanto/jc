r"""jc - JSON Convert MBOX parser

Usage (cli):

    $ echo "/path/to/mailbox.mbox" | jc --jwt

Usage (module):

    import jc
    result = jc.parse('mbox', path_to_mbox_file)

Schema:

    {
        "subject": string
        "from": string
        "to": [string, string, ...]
        "date": string # datetime
        "cc": [string, string, ...]
        "bcc": [string, string, ...]
        "body": string
    }
"""
from typing import Dict
import mailbox
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses
import re

class info():
    """Provides parser metadata (version, author, etc.)"""
    version = '1.0'
    description = 'Mbox email file parser'
    author = 'Galih Rivanto'
    author_email = 'galih.rivanto@gmai.com'
    compatible = ['linux']
    tags = ['email', 'mbox']

__version__ = info.version


def parse(
    data: str,
    raw: bool = False,
    quiet: bool = False
) -> Dict:
    """
    Main text parsing function

    Parameters:

        data:        (string)  text data to parse
        raw:         (boolean) output raw data
        quiet:       (boolean) suppress warning messages

    Returns:

        Dictionary
    """

    # Function to convert email message to a dictionary
    def email_to_dict(message):
        return {
            "subject": message.get("subject", ""),
            "from": message.get("from", ""),
            "to": split_addresses(message.get("to", "")),
            "date": message.get("date", ""),
            "cc": split_addresses(message.get("cc", "")),
            "bcc": split_addresses(message.get("bcc", "")),
            "body": get_body(message)
        }

    # Function to extract the body from an email message
    def get_body(message):
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
        else:
            return message.get_payload(decode=True).decode(message.get_content_charset() or 'utf-8', errors='replace')

    # Function to split email addresses into a list
    def split_addresses(addresses):
        if addresses:
            return [addr for _, addr in getaddresses([addresses])]
        return []
    
    def clean_whitespace(text):
        # Remove leading and trailing whitespace
        cleaned_text = text.strip()

        # Replace multiple spaces, newlines, and tabs with a single space
        return re.sub(r'\s+', ' ', cleaned_text)

    # Load the mbox data (path of file)   
    mbox = mailbox.mbox(clean_whitespace(data), factory=lambda f: BytesParser(policy=policy.default).parse(f))
   

    # Convert each message to a dictionary and collect them
    emails = []
    for message in mbox:
        emails.append(email_to_dict(message))

    # Return the email data
    return emails