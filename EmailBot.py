import json
import imaplib
import smtplib
import email
from email.header import decode_header, make_header


class Emailer(object):
    def __init__(self, login='email_login.json'):
        # Parse json
        with open(login) as f:
            data = json.load(f)
        # Create imao client
        self.client = imaplib.IMAP4_SSL(data['server'])
        self.client.login(data['username'], data['passwd'])

        # We want to save the credentials so we can seen the emails using smtp later.
        self.server = data['server']
        self.username = data['username']
        self.passwd = data['passwd']

        self.client.select('INBOX', readonly=False)

    def __del__(self):
        self.client.close()

    def search(self, key_word='Summarize'):
        # We want to search for unseen mail that satisfies the subject keyword provided.
        typ, msg_ids = self.client.search(None, f'(UNSEEN SUBJECT "{key_word}")')
        return msg_ids

    def get_email_data(self, id):
        typ, msg_data = self.client.fetch(id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1].decode('utf-8'))
                subject = str(make_header(decode_header(msg['subject'])))
                sender = str(make_header(decode_header(msg['from'])))
                if msg.is_multipart():
                    for payload in msg.get_payload():
                        return sender, subject, payload.get_payload(decode=True).decode('utf-8')
                else:
                    return sender, subject, msg.get_payload(decode=True).decode('utf-8')

    def send_email(self, recipient, subject, body):
        new_message = email.message.Message()
        new_message.set_unixfrom('pymotw')
        new_message['Subject'] = subject
        new_message['From'] = self.username
        new_message['To'] = recipient
        new_message.set_payload(f'{body}\n')

        smtp_obj = smtplib.SMTP(self.server, 587)
        smtp_obj.ehlo()
        smtp_obj.starttls()
        smtp_obj.login(self.username, self.passwd)
        smtp_obj.sendmail(self.username, recipient, str(new_message).encode('utf-8'))

        smtp_obj.quit()

    def close(self):
        self.client.close()