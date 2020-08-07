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
summary while keeping it at the desired length, the knapsack problem 
is used to find the optimization.

In the future I would like to add an automatic method of find the best percentag.
Instead of it being a required parameter.

## Example Usage
For the following example I will use essay found [here](http://editions-hache.com/essais/kaczynski/kaczynski2.html),
as `sample_text.txt`. 

With the following code. We can load the summarizer and create our summary
```python
from summarize import Summarizer 

# Load text
text_file = open('sample_text.txt', encoding="utf8")
sample_text = str(text_file.read())

# Remove unwanted text in the essay. ie '(fr)'
sample_text = sample_text.replace('(fr) ', '')

# Load document class
summarizer = Summarizer(sample_text)

```
Once loaded we can generate a summary that is 0.5% the original size. `ret_as='str'` tells the summarizer to return the
result as a single string
```python
summary = summarizer.get_optimal_subset_by_percent_words(.005, ret_as='str')
```
Because the original essay is around 34,000 words our summary is still fairly long so I have include only the first 7
sentence below.
```txt
The industrial-technological system may survive or it may break down.
We therefore advocate a revolution against the industrial system.
THE POWER PROCESS 33.
The power process has four elements.
But in modern industrial society the problem has become particularly acute.
DISRUPTION OF THE POWER PROCESS IN MODERN SOCIETY 59.
One may become angry, but modern society cannot permit fighting.
```
We can see that there are multiple very important key 
sentences, so overall the summarizer is a success. Especially for such a small percentage of the original document. 
One thing to notice is in our summary we have two title as sentences. This is a side effect of how words and sentences
are valued. As subtitles or titles tend to have very commonly used words.

To see an example using number of words rather than a percentage look in `scripts/test_summarizer.py`

## Chrome Extension
Readme explanation coming soon!! But it should still work.

## Email Bot
Provided a credentials file with the email login information and server, 
look at the example credential file for an example of the structure, 
the `SummarizerBot.py` should work. The emails sent to the bot account 
should have the following subject: "Summarize: \<Title or description\>"
and the body of the email should contain an article or essay in plain 
text. Alternatively, the header can be "Summarize: URL" and the body 
should be the url or urls if multiple. Stories work but wont work well. I May or may not have a 
bot running under the email `ijorquer7974@gmail.com` for anyone to test 
it out. The bot will email back a summary that is 20% the original size
of the article.

## Desktop Application
To compile a desktop application run the following 
command, in the command line,
```
pyinstaller --onefile --hidden-import inscriptis SummarizerApplication.py
```
Once compiled either drag and drop desired file onto app to be summarized. 
Or copy the desired link, or text, and run the application, and 
the executable will automatically use the copied data from 
the clipboard. It is important to note that coping text 
directly can be prone to many strange issues and isn't 
recommended.