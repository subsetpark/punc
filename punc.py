import zulip
import sys, re
from collections import Counter
from pymongo import MongoClient
from nltk.tokenize import RegexpTokenizer
import nltk.data

def update_count(text, stream):
    """
    Increment our counter with all the punctuation.
    """
    
    tokens  = map(sanitize_token, tokenizer.tokenize(text))
    tokens.extend(['ALLCAPS' for t in sent_detector.tokenize(text) if allcaps(t)])
    associations[stream].update(tokens)
    update_table(stream)

def allcaps(t):
    allcaps = re.compile("[^a-z]+$")
    if re.match(allcaps, t):
        return True
    else:
        False

def update_table(counter):
    current_record = {}
    for element in associations[counter].keys():
        current_record[element] = associations[counter][element]
    punc_db.update({'name':counter},{"$set": {"PUNC": current_record}}, upsert=True)

def sanitize_token(t):
    TOKEN_NAMES = {
     "!" : "BANG"
    ,"?" : "QUESTION"
    ,"." : "FULLSTOP"
    ,":)": "SMILEY"
    ,":(": "FROWNY" }
    if t in TOKEN_NAMES.keys():
        return TOKEN_NAMES[t]
    else:
        return t

def print_and_add(message):
    content = message['content']
    stream = message['display_recipient']
    print message['sender_short_name'] + ": " + content 
    update_count(content, stream)
    print associations[stream]


client = zulip.Client(email="punc-bot@students.hackerschool.com",
                    api_key="7rZVIQkv5XIAEZYOWW61imFZdSieAeGQ")
db_connection = MongoClient('localhost', 27017)
db = db_connection[__name__]
punc_db = db.punc
tokenizer = RegexpTokenizer('[?!.]|:\)|:\(')
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
associations = {}

for sub in client.list_subscriptions()['subscriptions']:
    stream = sub['name']
    if not punc_db.find_one({'name':stream}):
        punc_db.insert({'name':stream})
    
    db_record = punc_db.find_one({'name':stream})
    punc_record = db_record.get('PUNC') or {}
    associations[stream] = Counter(punc_record) 

def run():
    client.call_on_each_message(print_and_add)

      

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    run()
    