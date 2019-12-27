import unidecode
import numpy as np
import re


stop_words = ["", " ", "\n", "i", "me", "my", "oh", 'mr', 'mrs', "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
# states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']


class Document(object):
    endings = [['. ', '."', '.\n', '.)'],  # Normal sentence endings
               ['! ', '!"', '!\n', '!)'],  # exclamation sentences
               ['? ', '?"', '?\n', '?)'],  # Questions
               [' ', '-']]  # word endings. Node we don't need to consider punctuation as long as there is still a space

    def __init__(self, doc, title=None):
        """
        Takes in a string of the text. Honestly this could all be done with a single function but that get messy
        :param doc: text
        :param title: optional title
        """
        self.sentences = []
        self.sentence_len = []
        self.sentences_val = []
        self.words = {}
        self.total_words = 0
        # Covert document to unicode
        self.document = unidecode.unidecode(doc)
        # Replace all white space with just single spaces
        self.document = re.sub(r'[ \t\n\r]+', ' ', self.document)

        # If a title is provided we want to parse that for better results
        self.subject = str(title)
        if title is not None:
            self.title = title.lower().split(' ')
        else:
            self.title = []
    
    @staticmethod
    def clean_word(w):
        return re.sub(r'[^\w]', '', w.strip().lower())

    def parse_text(self):
        """
        Parses text into sentences and give each sentence a value
        :return:
        """
        s_start = 0
        w_start = 0
        # We want to iterate through the chars to split into words and sentences.
        for i in range(0, len(self.document)):
            # This will tell us if we ran into a sentence or not
            sen_val = None
            # our '.' case. normal sentence. watch for acronyms and cases like 'Mr.'
            if self.document[i:i+2] in self.endings[0]:
                if (i > 2 and
                    (self.document[i-2:i] == 'Mr' or self.document[i-2:i] == 'Dr' or self.document[i-2] == '.')) or \
                        (i > 3 and (self.document[i-3:i] == 'Mrs' or self.document[i-3:i].lower() == ' vs')):
                    continue  # if its not the end of a sentence. This wont always be true. but
                sen_val = 0
            elif self.document[i:i + 2] in self.endings[1]:  # '!' case
                sen_val = 2
            elif self.document[i:i + 2] in self.endings[2]:  # '?' case
                sen_val = 4
            elif self.document[i] in self.endings[3] and i-w_start > 0:  # End of word. ignore just a space.
                pass
            else:
                continue  # Still in a word

            # Clean word of punctuation and case
            # In the future we can add something that simplifies a word like 'cities' to 'city'
            word = self.clean_word(self.document[w_start:i])

            if sen_val is not None:  # If it was the end of a sentence add sentence to lists
                self.sentences.append(self.document[s_start:i])  # TODO: should this be i+1?
                self.sentences_val.append(sen_val)  # based on type we give the sentence a starting score
                self.sentence_len.append(len(re.split(' |-', str(self.sentences[-1]))))
                s_start = i + 2
                w_start = i + 2
            else:
                w_start = i + 1

            # Add word to total. Used to find the desired output size
            self.total_words += 1
            # Count number of each word
            if word not in stop_words:
                if word in self.words:
                    self.words[word] += 1
                else:
                    self.words[word] = 1
        # Now we have the sentences and the word counts.
        # we want to adjust the words dict to a point system instead of just the numbers of occurrences.
        # As of now the score is based on how many standard deviations from the mean, the number of occurrences is.
        # Every word gets one point as wew value longer sentences.

        # These variables represent the adjustments. all fractional point are rounded down
        std_mult = 1  # How many point a word get for each standard deviation above occurrences mean it is
        under_mean = 1  # For any word with number of occurrences bellow the mean, this is added
        per_word = 0  # baseline number of points added for every word
        char_mult = 1/3  # For every character in a word above 6 character it will receive this many points.
        title_word = 3  # Additional points if word is in the title
        word_thres = 5  # Only sentences with this many or more words will be considered
        sw_val = 0  # Number of points a sentence gets for each stop word

        mean = np.array([self.words[k] for k in self.words]).mean()
        mean_squared = np.array([self.words[k]*self.words[k] for k in self.words]).mean()
        # For some reason this gave me slightly different values than np.std, probably just a rounding issue
        std = np.sqrt(mean_squared - mean)
        for word in self.words:
            if self.words[word] < mean + std or std == 0.0:
                self.words[word] = max(0, int(char_mult * (len(word)-6))) + under_mean + per_word
            else:
                self.words[word] = int(std_mult * ((self.words[word] - mean)/std)) + \
                                   max(0, int(char_mult * (len(word)-6))) + per_word

        # We want to consider the title too. we will give an addition amount of points for words in the title.
        for w in self.title:
            word = self.clean_word(w)
            if word in self.words:
                self.words[word] += title_word

        # now we want to give each sentence its own value
        for s in range(0, len(self.sentences)):
            if self.sentence_len[s] < word_thres:
                self.sentences_val[s] = 0
                continue
            for w in re.split(' |-', self.sentences[s]):
                word = self.clean_word(w)
                # For each word in the sentence we add the value
                if word not in stop_words:
                    if word in self.words:
                        self.sentences_val[s] += self.words[word]
                    else:
                        # this should never happen. If it does its treated as a stop word
                        print('*** ' + word)
                        self.sentences_val[s] += sw_val
                else:
                    self.sentences_val[s] += sw_val

    def create_document_summary(self, percent_words=0.0, num_words=0):
        if percent_words == 0 and num_words == 0:
            return "Error: summary size not specified"
        # parse data to get points for each sentence
        self.parse_text()
        if percent_words != 0.0:
            return self.opt_summary(self.sentences, self.sentence_len, self.sentences_val,
                                   int(percent_words*self.total_words))
        else:
            return self.opt_summary(self.sentences, self.sentence_len, self.sentences_val, num_words)

    @staticmethod
    def opt_summary(sentence_arr, w_arr, v_arr, num_words):
        """
        This is identical to the solution for the Knapsack problem.
        Copied from class work
        """
        def recover_solution(i, j):
            solution = []
            while i > 0 and j > 0:
                if opt[i, j] == opt[i-1, j]:
                    i -= 1
                else:
                    solution.append(sentence_arr[i-1])
                    j -= w_arr[i-1]
                    i -= 1
            return solution[::-1]
        if len(w_arr) != len(v_arr):
            return None
        # This initializes our base cases to 0. Because we iterate through all items everything can be zero
        opt = np.array([[0 for _ in range(num_words + 1)] for _ in range(len(w_arr) + 1)])
        # This initializes our base cases

        for i in range(1, len(w_arr) + 1):
            for j in range(1, num_words + 1):
                # It is important to not that every time we access the opt array we use i and j and ever time
                # we access the w_arr ir v_arr we use i-1 or j-1. This is because item 1 is index 0.
                if j - w_arr[i - 1] >= 0:
                    opt[i, j] = max(opt[i - 1, j], opt[i - 1, j - w_arr[i - 1]] + v_arr[i - 1])
                else:
                    opt[i, j] = opt[i - 1, j]
        return recover_solution(len(w_arr), num_words)


if __name__ == '__main__':
    pass
    # I will leave these comments here as an example of the possible usage
    # text_file = open('sample_text.txt', encoding="utf8")
    # text_file = open('prideandprejudilce.txt', encoding="utf8")
    # text_file = open('test.txt', encoding="utf8")

    # Load text
    # sample_text = str(text_file.read())

    # Remove unwanted text in the essay. ie '(fr)'
    # sample_text = sample_text.replace('(fr) ', '')

    # Load document class
    # doc = Document(text, headline)
    # doc = Document(sample_text, 'Industrial Society and Its Future')
    # doc = Document(sample_text, 'Boeing Can’t Fly Its 737 Max, but It’s Ready to Sell Its Safety')
    # doc = Document(sample_text, 'pride and prejudice')

    # Find summary
    # summary = doc.create_document_summary(percent_words=.1)
    # summary = doc.create_document_summary(num_words=200)

    # Write out summary and print score
    # w_file = open('output.txt', 'w+')
    # w_file.write('.\n'.join(summary) + '.')
