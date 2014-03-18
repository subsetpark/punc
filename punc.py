import zulip
import re, itertools
from collections import Counter
from pymongo import MongoClient
from nltk.tokenize import RegexpTokenizer
import nltk.data

def sanitize_token(t):
    TOKEN_NAMES = {
     "!" : "BANG"
    ,"?" : "QUESTION"
    ,"." : "FULLSTOP"
    ,":)": "SMILEY"
    ,":(": "FROWNY" 
    ,";)": "WINKY"
}
    return TOKEN_NAMES.get(t) or t

def allcaps(t):
    allcaps = re.compile("[^a-z]+$")
    if re.match(allcaps, t):
        return True
    else:
        return False

class Punc(object):

    def __init__(self, email, api):
        self.client = zulip.Client(email, api)
        self.db_connection = MongoClient('localhost', 27017)
        self.db = self.db_connection['punc']
        self.punc_db = self.db.counters
        self.tokenizer = RegexpTokenizer(r'\?$|\!$]|:\)|:\(|;\)|\.$')
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.counters = {}
        self.sync_db()

    def print_and_add(self, message):
        """
        Read out a new message and process it.
        """
        content = message['content']
        stream = message['display_recipient']
        print message['sender_short_name'] + ": " + content 
        self.update_count(content, stream)
        print stream + " " + str(self.counters[stream])

    def update_count(self, text, stream):
        """
        Process a new line of text from Zulip.
        """
        sentences = self.sent_detector.tokenize(text)
        tokens = [sanitize_token(token) 
                    for sentence in sentences 
                    for token in self.tokenizer.tokenize(sentence)]
        tokens.extend(['ALLCAPS' for t in sentences if allcaps(t)])
        self.counters[stream].update(tokens)
        self.counters[stream].update({'sentences': len(sentences)})
        self.update_table(stream)

    def update_table(self, counter):
        current_record = {}
        for element in self.counters[counter].keys():
            current_record[element] = self.counters[counter][element]
        self.punc_db.update({'name':counter},{"$set": {"PUNC": current_record}}, upsert=True)

    def sync_db(self):
        for sub in self.client.list_subscriptions()['subscriptions']:
            stream = sub['name']
            if not self.punc_db.find_one({'name':stream}):
                self.punc_db.insert({'name':stream})
            
            db_record = self.punc_db.find_one({'name':stream})
            punc_record = db_record.get('PUNC') or {}
            self.counters[stream] = Counter(punc_record) 

    def run(self):
        self.client.call_on_each_message(self.print_and_add)

if __name__ == "__main__":
    import os
    if 'PUNC_EMAIL' in os.environ:
        config_email = os.environ['PUNC_EMAIL']
    if 'PUNC_KEY' in os.environ:
        config_api = os.environ['PUNC_KEY']
    punc = Punc(config_email, config_api)
    punc.run()
    