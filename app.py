from flask import Flask
import punc
import pymongo
import collections
app = Flask(__name__)

db_connection = pymongo.MongoClient('localhost', 27017)
db = db_connection.punc.counters

counters = {}
all_counts = collections.Counter()
averages= {}


def simple_sentiment(counter):
    if counter.get('FULLSTOP') or 0 > max(counter.get('QUESTION') or 0, counter.get('BANG') or 0):
        return "is very forthright."
    elif counter.get('QUESTION') or 0 > max(counter.get('FULLSTOP') or 0, counter.get('BANG') or 0):
        return "is full of questions."
    elif counter.get('BANG') or 0 > max(counter.get('FULLSTOP') or 0, counter.get('QUESTION') or 0):
        return "is very excited."
    else:
        return "is still unclear."

def analyze_sentiment(name, counter):
    descriptors = {
        'QUESTION': 'confused',
        'FULLSTOP': 'forthright',
        'BANG': 'excited',
        'SMILEY': 'cheery',
        'FROWNY': 'glum',
        'ALLCAPS': 'emphatic'
    }
    stream_analysis = ""
    for token, count in counter.iteritems():
        ratio = float(count) / counter['sentences'] 
        if token == 'sentences':
            continue
        elif (1.5 * averages[token]) < ratio:
            stream_analysis += name + " is very " + descriptors[token] + ". "
        elif averages[token] < ratio <= (1.5 * averages[token]):
            stream_analysis += name + " is rather " + descriptors[token] + ". "
    if not stream_analysis:
        stream_analysis = name + " is pretty dull."
    return stream_analysis
 

def update_counters():
    for f in db.find():
        counters[f.get('name')] = f.get('PUNC') or {}
    for s, c in counters.iteritems():
        all_counts.update(c)
    for token, count in all_counts.iteritems():
        averages[token] = float(count) / all_counts['sentences']


    print str(all_counts)
@app.route("/")
def sentiment_analysis():
    update_counters()
    response = "<html><body>"
    for name, counter in counters.iteritems():
        print name + ": " + str(counter)
        response += ("<p>" + analyze_sentiment(name, counter) + "</p>")

    response += "</body></html>"
    return response

if __name__ == "__main__":
    app.run()