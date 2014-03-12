import zulip
import re
from collections import Counter
from pymongo import MongoClient
from nltk.tokenize import RegexpTokenizer
import nltk.data

def print_and_add(message):
    """
    Read out a new message and process it.
    """
    content = message['content']
    stream = message['display_recipient']
    print message['sender_short_name'] + ": " + content 
    update_count(content, stream)
    print stream + " " + str(counters[stream])

def update_count(text, stream):
    """
    Process a new line of text from Zulip.
    """
    sentences = sent_detector.tokenize(text)
    tokens  = map(sanitize_token, tokenizer.tokenize(text))
    tokens.extend(['ALLCAPS' for t in sentences if allcaps(t)])
    counters[stream].update(tokens)
    counters[stream].update({'sentences': len(sentences)})
    update_table(stream)

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

def update_table(counter):
    current_record = {}
    for element in counters[counter].keys():
        current_record[element] = counters[counter][element]
    punc_db.update({'name':counter},{"$set": {"PUNC": current_record}}, upsert=True)

client = zulip.Client(email="punc-bot@students.hackerschool.com",
                    api_key="7rZVIQkv5XIAEZYOWW61imFZdSieAeGQ")
db_connection = MongoClient('localhost', 27017)
db = db_connection['punc']
punc_db = db.counters
tokenizer = RegexpTokenizer('[?!.]|:\)|:\(|;\)')
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
counters = {}

for sub in client.list_subscriptions()['subscriptions']:
    stream = sub['name']
    if not punc_db.find_one({'name':stream}):
        punc_db.insert({'name':stream})
    
    db_record = punc_db.find_one({'name':stream})
    punc_record = db_record.get('PUNC') or {}
    counters[stream] = Counter(punc_record) 

def run():
    client.call_on_each_message(print_and_add)
     
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    run()
    