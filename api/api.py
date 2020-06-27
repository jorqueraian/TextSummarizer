import flask
from flask import request, jsonify

import Summarize
app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Text Summarizer</h1><p>This site is a prototype API</p>"

@app.route('/api/summarizetext', methods=['GET'])
def api_summarize_text():
    if 'text' in request.args:
        text = str(request.args['text'])
    else:
        return "Error: No text field provided. Please specify text."

    if 'headline' in request.args:
        headline = str(request.args['headline'])
    else:
        return "Error: No headline provided. Please specify a headline."

    # Create an empty list for our results
    doc = Summarize.Document(text, headline)
    summary = doc.create_document_summary(percent_words=.1)

    return '.\n'.join(summary) + '.'

app.run()
