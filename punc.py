import zulip
import sys
from collections import Counter
from pymongo import MongoClient
from nltk.tokenize import RegexpTokenizer


client = zulip.Client(email="punc-bot@students.hackerschool.com",
                    api_key="7rZVIQkv5XIAEZYOWW61imFZdSieAeGQ")

db_connection = MongoClient('localhost', 27017)
db = db_connection[__name__]
punc_db = db.punc
tokenizer = RegexpTokenizer('[?!.]')
associations = {}

for sub in client.list_subscriptions()['subscriptions']:
    stream = sub['name']
    associations[stream] = Counter(punc_db.find_one({'name':stream}))

def update_table(counter):
    document = punc_db.find_one({"name": counter})
    for element in associations[counter].keys():
        document[element] = associations[counter][element]
    punc_db.save(document)

def update_db():
    for counter in associations:
        update_table(counter)

def sanitize_tokens(t):
    for index, token in enumerate(t):
        if token == '.':
            t[index] = 'FULLSTOP'
        elif token == '?':
            t[index] = 'QUESTION'
        elif token == '!':
            t[index] = 'BANG'
    return t

# response = client.register(event_types=["messages"])
def print_and_add(message):
    stream = message['display_recipient']
    print message['sender_short_name'] + ": " + message['content']
    t  = sanitize_tokens(tokenizer.tokenize(message['content']))
    associations[stream].update(t)

if __name__ == "__main__":
    client.call_on_each_message(print_and_add)

# client.do_api_query({'anchor':'18202209', 'num_before':'100', 'num_after':'0', 'narrow': [['stream', 'python']]}, event-types=["messages"], 'https://zulip.com/api/v1/messages', method='GET')