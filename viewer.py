from flask import Flask, render_template
import punc
import pymongo
import collections
import json

app = Flask(__name__)
app.config.from_object(__name__)

class Viewer(object):
    """
    The Punc Viewer pulls Punc bot information from a MongoDB database and analyzes them
    within a Flask app. 
    """
    def __init__(self, db_ip):
        db_connection = pymongo.MongoClient(db_ip, 27017)
        self.db = db_connection.punc.counters

        self.counters = {}
        self.all_counts = collections.Counter()
        self.averages= {}

    def update_counters(self):
        self.all_counts.clear()
        for f in self.db.find():
            self.counters[f.get('name')] = f.get('PUNC') or {}
        for _, c in self.counters.iteritems():
            self.all_counts.update(c)
        for token, count in self.all_counts.iteritems():
            self.averages[token] = float(count) / self.all_counts['sentences']

        print "all counts: " + str(self.all_counts)

    def analyze_sentiment(self, counter):
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
            average = self.averages[token]
            if token == 'sentences':
                continue
            if token not in descriptors:
                continue
            if (ratio / average) > 2:
                stream_analysis.append("is very <em>%s.</em>" % descriptors[token])
            elif (ratio / average) > 1:
                stream_analysis.append("is rather <em>%s.</em>" % descriptors[token])
        if not stream_analysis:
            stream_analysis = ["is pretty dull."]
        if 'glum' in " ".join(stream_analysis) and 'cheery' in " ".join(stream_analysis):
            stream_analysis.append("is just full of emotion!")
        return stream_analysis

    def prepare_graphs(self):
        graph_data = []
        for name, counter in self.counters.iteritems():
            counter_data = {'key' : name, 'values' : []}
            for token, count in iter(sorted(counter.iteritems())):
                if token == 'sentences':
                    continue
                ratio = float(count) / counter['sentences']
                counter_data['values'].append({'x' : token, 'y' : ratio}) 
            graph_data.append(counter_data)

        average_data = {'key' : 'avg', 'values' : []}
        for token, count in iter(sorted(self.all_counts.iteritems())):
            if token == 'sentences':
                continue
            average_data['values'].append({'x' : token, 'y' : self.averages[token]})
        return graph_data, average_data

import os
if 'PUNC_DB' in os.environ:
    db_ip = os.environ['PUNC_DB'] 
viewer = Viewer(db_ip)

@app.route("/")
def sentiment_analysis():
    viewer.update_counters()
    entries = [{'name': name, 'sentiment': viewer.analyze_sentiment(counter)} 
                for name, counter in viewer.counters.items()]
    for name, counter in viewer.counters.iteritems():
        print name + ": " + str(counter)
    graph_data, average_data = viewer.prepare_graphs() 
    
    return render_template('counters.html',entries=entries, data=json.dumps(graph_data), avg=json.dumps(average_data))

if __name__ == "__main__":
    app.debug = True
    app.run()