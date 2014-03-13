from flask import Flask, render_template
import punc
import pymongo
import collections
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

db_connection = pymongo.MongoClient('localhost', 27017)
db = db_connection.punc.counters

counters = {}
all_counts = collections.Counter()
averages= {}

def update_counters():
    all_counts.clear()
    for f in db.find():
        counters[f.get('name')] = f.get('PUNC') or {}
    for _, c in counters.iteritems():
        all_counts.update(c)
    for token, count in all_counts.iteritems():
        averages[token] = float(count) / all_counts['sentences']

    print "all counts: " + str(all_counts)

def analyze_sentiment(counter):
    """
    Compare the relative frequency of each token in each stream. If it's more than the average 
    ratio (calculated against no. of sentences) then print out a descriptor.
    """
    descriptors = {
        'QUESTION': 'confused'
       ,'FULLSTOP': 'forthright'
       ,'BANG': 'excited'
       ,'SMILEY': 'cheery'
       ,'FROWNY': 'glum'
       ,'ALLCAPS': 'emphatic'
       ,'WINKY': 'coy'
    }
    stream_analysis = []
    for token, count in counter.iteritems():
        ratio = float(count) / counter['sentences']
        average = averages[token]
        # import pdb
        # pdb.set_trace() 
        if token == 'sentences':
            continue
        if not descriptors[token]:
            continue
        if (ratio / average) > 2:
            stream_analysis.append("is very %s." % descriptors[token])
        elif (ratio / average) > 1:
            stream_analysis.append("is rather %s." % descriptors[token])
    if not stream_analysis:
        stream_analysis = ["is pretty dull."]
    return stream_analysis

@app.route("/")
def sentiment_analysis():
    update_counters()
    entries = [{'name': name, 'sentiment': analyze_sentiment(counter)} 
                for name, counter in counters.iteritems()]
    for name, counter in counters.iteritems():
        print name + ": " + str(counter)
    
    return render_template('counters.html',entries=entries)

if __name__ == "__main__":
    app.run()