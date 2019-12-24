import unidecode
import numpy as np
import re

stop_words = ["", " ", "\n", "i", "me", "my", 'mr', 'mrs', "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]


class Document(object):
    endings = [['. ', '."', '.\n'],  # Normal sentence endings
               ['! ', '!"', '!\n'],  # exclamation sentences
               ['? ', '?"', '?\n'],  # Questions
               [' ', '-']]  # word endings. Node we don't need to consider punctuation as long as there is still a space
    sentences = []
    sentence_len = []
    sentences_val = []
    words = {}
    total_words = 0

    def __init__(self, doc, title=None):
        """
        Takes in a string of the text
        :param doc: text
        :param title: optional title
        """
        self.document = unidecode.unidecode(doc)
        # Replace all white space with just single spaces
        split_up = re.split(' |\n|\t', self.document)
        split_up.remove('')
        self.document = ' '.join(split_up)
        if title is not None:
            self.title = title.lower().split(' ')
        else:
            self.title = []

    @staticmethod
    def clean_word(w):
        return w.strip().lower().replace(',', '').replace('"', '').replace('.', '').replace("'", '').replace(':', '')\
            .replace('(', '').replace(')', '').replace('[', '').replace(']', '')

    def parse_text(self):
        """
        Parses text into sentences and give each sentence a value
        :return:
        """
        s_start = 0
        w_start = 0
        # We want to iterate through the chars to split into words and sentences.
        for i in range(0, len(self.document)):
            sen_val = None
            # our '.' case. normal sentence. watch for acronyms and cases like 'Mr.'
            if self.document[i:i+2] in self.endings[0]:
                if i > 2 and (self.document[i-2:i] == 'Mr' or self.document[i-2] == '.') or \
                        i > 3 and self.document[i-3:i] == 'Mrs':
                    continue  # if its not the end of a sentence. This wont always be true. but
                sen_val = 0
            elif self.document[i:i + 2] in self.endings[1]:  # '!' case
                sen_val = 2
            elif self.document[i:i + 2] in self.endings[2]:  # '?' case
                sen_val = 4
            elif self.document[i] in self.endings[3] and i-w_start > 0:  # Word. ignore just a space.
                pass
            else:
                # If not sentence or word we want to continue
                continue
            # Clean word of punctuation and case
            word = self.clean_word(self.document[w_start:i])
            # add sentence
            if sen_val is not None:
                self.sentences.append(self.document[s_start:i])
                self.sentences_val.append(sen_val)  # based on type we give the sentence a starting score
                self.sentence_len.append(len(re.split(' |-', self.sentences[-1])))
                s_start = i + 2
                w_start = i + 2
            else:
                w_start = i + 1

            # Add word to total. Used to find the desired output size
            self.total_words += 1
            if word not in stop_words:
                if word in self.words:
                    self.words[word] += 1
                else:
                    self.words[word] = 1
        # Now we have the sentences and the word counts.
        # we want to adjust the words dict to a point system.
        # As of now, its based on occurrence relative to the mean.
        # Every word gets one point as wew value longer sentences. And the more occurrences relative to the standard
        # deviation the more points it gets.
        mean = np.array([self.words[k] for k in self.words]).mean()
        mean_squared = np.array([self.words[k]*self.words[k] for k in self.words]).mean()
        # For some reason this gave me slightly different values than np.std, probably just a rounding issue
        std = np.sqrt(mean_squared - mean)

        for word in self.words:
            if self.words[word] < mean:
                self.words[word] = 1
            else:
                self.words[word] = int((self.words[word] - mean)/std) + 1

        # We want to consider the title too. we will give an addition 3 points for words in the title.
        for w in self.title:
            word = self.clean_word(w)
            if word in self.words:
                self.words[word] += 3

        # now we want to give each sentence its own value
        for s in range(0, len(self.sentences)):
            for w in re.split(' |-', self.sentences[s]):
                word = self.clean_word(w)
                # For each word in the sentence we add the value
                if word not in stop_words:
                    if word in self.words:
                        self.sentences_val[s] += self.words[word]
                    else:
                        self.sentences_val[s] += 1

    def document_summary(self, percent_words=0.0, num_words=0):
        doc.parse_text()
        if num_words == 0:
            return doc.opt_summary(self.sentences, self.sentence_len, self.sentences_val,
                                   int(percent_words*self.total_words))
        else:
            return doc.opt_summary(self.sentences, self.sentence_len, self.sentences_val, num_words)

    @staticmethod
    def opt_summary(sentence_arr, w_arr, v_arr, num_words):
        """
        Knapsack problem
        """
        def recover_solution(i, j):
            # print(opt[i, j])
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
    # text_file = open('sample_text.txt', encoding="utf8")
    text_file = open('prideandprejudice.txt', encoding="utf8")

    # Load text
    sample_text = str(text_file.read())

    # Remove unwanted text in the essay. ie '(fr)'
    sample_text = sample_text.replace('(fr)', '')

    # Load document class
    # doc = Document(sample_text, 'Industrial Society and Its Future')
    doc = Document(sample_text, 'pride and prejudice')

    # Find summary
    summary = doc.document_summary(percent_words=.005)
    # summary = doc.document_summary(num_words=200)

    # Write out summary and print score
    w_file = open('output.txt', 'w+')
    w_file.write('. '.join(summary) + '.')
    print('Summary saved')



