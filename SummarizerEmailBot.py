from Summarize import Document
from EmailBot import Emailer
import time

if __name__ == '__main__':
    email_client = Emailer()
    while True:
        # Retrieve unseen emails with 'Summarize' in the subject. Returns IDs in space separated str form.
        emails = email_client.search()[0].decode()

        # If the string is empty there are no new emails
        if len(emails) == 0:
            print('No emails')
            time.sleep(10)
            continue

        print(f'Emails to process: {emails}')
        sender, subject, body = email_client.get_email_data(emails.split(' ')[0])
        print(f'Email received from: {sender}')

        # Load document class with body text
        document = Document(str(body), subject.replace('Summarize: ', ''))

        # Find summary, that is twenty percent the size
        summary = document.create_document_summary(percent_words=.2)

        sender = sender.split('<')[-1].split('>')[0]
        email_client.send_email(sender, subject.replace('Summarize', 'Completed Summary'), '.\n'.join(summary))
        # email_client.close()
        print('Summary sent')
        # time.sleep(2)
