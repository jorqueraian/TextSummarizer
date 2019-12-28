from Summarize import Document
from EmailBot import body_from_website
import sys
import os
from tkinter import Tk

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Here we want to use the params
        with open(sys.argv[1], encoding="utf8") as file:
            text = str(file.read())
        subj = ''
    else:
        # If no file was dragged in or anything we want to use what ever is in the clipboard
        tk = Tk()
        tk.withdraw()
        copied_text = tk.clipboard_get()

        subj, text = body_from_website(copied_text.lower())
        if text == '':
            if len(copied_text) > 100:
                text = copied_text
                subj = ''
            else:
                print(f'Invalid Input: {copied_text}')
                input('Press enter to continue...')
                sys.exit()
        else:
            print(f'Loading text from: {copied_text}')

    document = Document(text, subj)

    summary = document.create_document_summary(percent_words=.15)

    # Generate response

    response_body = 'Title: ' + document.subject + '\n\n'
    if len(summary) != 0:
        response_body += '.\n'.join(summary)
    else:
        response_body += 'Text Too Short'
    response_body += '\n\n--------------\n\n'

    print(response_body)

    loc = 'output.txt'
    with open(loc, "w") as output_file:
        output_file.write(str(response_body))

    print(f'Summary created and save to {os.path.abspath(loc)}')
    input('Press enter to continue...')

