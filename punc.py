import zulip
import sys
import re, math, collections
from nltk.tokenize import RegexpTokenizer


client = zulip.Client(email="punc-bot@students.hackerschool.com",
                    api_key="7rZVIQkv5XIAEZYOWW61imFZdSieAeGQ")

client.add_subscriptions([ {"name": "python"},
                           {"name": "haskell"},
                           {"name": "erlang"},
                           {"name": "ruby"}])

associations = {
    'ruby': collections.Counter(),
    'haskell': collections.Counter(),
    'python': collections.Counter(),
    'erlang': collections.Counter(),
    'test-bot': collections.Counter()
}
tokenizer = RegexpTokenizer('[?!.]')
# response = client.register(event_types=["messages"])
def print_and_add(message):
    stream = message['display_recipient']
    print message['sender_short_name'] + ": " + message['content']
    t  = tokenizer.tokenize(message['content'])
    associations[stream].update(t)
    print associations
client.call_on_each_message(print_and_add)

# client.do_api_query({'anchor':'18202209', 'num_before':'100', 'num_after':'0', 'narrow': [['stream', 'python']]}, event-types=["messages"], 'https://zulip.com/api/v1/messages', method='GET')