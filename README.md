# TextSummarizer
This is a script built to create shortened summaries from 
large amounts of text. Given a percentage or word count the
script finds the most valuable sentences to include. The 
importance of a sentence is determined by importance of 
each word. The importance of a word is determined by the 
number of occurrences of that word relative to the mean 
number of occurrences and the standard deviation. The value
of each word is added to find the value of a sentence. To
then find which sentences optimize the total value of the 
summary while keeping it at the desired length, a variation
of the knapsack problem is used for the optimization.

## Example Usage
Consider the following essay found [here](http://editions-hache.com/essais/kaczynski/kaczynski2.html),
in the form of a txt file. With the following code. We can load the document class
```python
# Load text
text_file = open('sample_text.txt', encoding="utf8")
sample_text = str(text_file.read())

# Remove unwanted text in the essay. ie '(fr)'
sample_text = sample_text.replace('(fr) ', '')

# Load document class
doc = Document(sample_text, 'Industrial Society and Its Future')

```
Once loaded we can generate a summary
```python
summary = doc.create_document_summary(percent_words=.005)
```
which results with the following summary that is 
.5% of the original text. Bellow is a shortened version
of the output
```txt
The industrial-technological system may survive or it may break down.
We therefore advocate a revolution against the industrial system.
But in modern industrial society the problem has become particularly acute.
DISRUPTION OF THE POWER PROCESS IN MODERN SOCIETY 59.
One may become angry, but modern society cannot permit fighting.
Modern society is in certain respects extremely permissive.
```
We can see that there are multiple very important key 
sentences. There are also a few sentences that seem 
meaningless as they are titles for each of the sub sections. This is consequence of 
priority technique used to determine the value of each word.

## Email Bot
Provided a credentials file with the email login information and server, 
look at the example credential file for an example of the structure, 
the `SummarizerBot.py` should work. The emails sent to the bot account 
should have the following subject: "Summarize: \<Title or description\>"
and the body of the email should contain an article or essay in plain 
text. Stories work but wont work well. I May or may not have a 
bot running under the email `ijorquer7974@gmail.com` for anyone to test 
it out. The bot will email back a summary that is 20% the original size
of the article.