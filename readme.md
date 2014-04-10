# punc
`punc` is a simple [Zulip](http://zulip.com) bot that collects basic sentiment data about its subscribed streams by counting punctuation. It is accompanied by a Flask web app that performs some simple sentiment analysis on the counter data.

## The bot
`punc` is a python script that runs a continuous blocking call to Zulip and receives all messages posted to its subscribed streams. It counts certain tokens in every message it receives: certain punctuation marks, smileys, and ALL CAPS SENTENCES. It writes this information to a mongodb database.

## The app
the `punc` web app is a Flask application that reads from `punc`'s database and runs some analysis on the running count. It compares the relative frequency of each token in a stream to the overall average frequency of that stream, and then uses this information to describe the overall tenor of that stream.

You can view the Punc web app at [punc.herokuapp.com](http://punc.herokuapp.com).

In other words, punc is data-driven journalism at its finest.