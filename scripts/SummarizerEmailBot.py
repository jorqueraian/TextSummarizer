from summarize import Summarizer
from EmailBot import Emailer, body_from_website
import time
import re

if __name__ == '__main__':
    while True:
        # For some reason the client will sometimes close its self
        email_client = Emailer()
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

        try:
            documents = []
            # Load document class with body text
            if subject.lower() == 'summarize: url':
                for url in re.split(r'[ \t\n\r]+', str(body)):
                    if url != '':
                        subj, text = body_from_website(url.lower())
                        if text != '':
                            documents.append(Summarizer(text))
            else:
                documents.append(Summarizer(str(body)))

            # Find summary, that is twenty percent the size
            summaries = []
            for document in documents:
                summaries.append(document.get_optimal_subset_by_percent_words(.15, ret_as='str'))

            # Create ew email body
            response_body = ''
            for i in range(len(documents)):
                response_body += 'Title: ' + subject
                response_body += '\n\n'
                if len(summaries[i]) != 0:
                    response_body += summaries[i]
                else:
                    response_body += 'Text Too Short'
                response_body += '\n\n--------------\n\n'

            sender = sender.split('<')[-1].split('>')[0]
            email_client.send_email(sender, subject.replace('Summarize', 'Completed Summary'), response_body)
            print('Summary sent')
            # time.sleep(2)

        except Exception as e:
            # sender = sender.split('<')[-1].split('>')[0]
            # email_client.send_email(sender, subject.replace('Summarize', 'ERROR'), 'Unexpected error')
            print(f'Error: {e}')
            time.sleep(2)
