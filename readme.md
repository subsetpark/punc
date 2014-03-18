# punc
`punc` is a simple [Zulip](http://zulip.com) bot that collects basic sentiment data about its subscribed streams by counting punctuation. It is accompanied by a Flask web app that performs some simple sentiment analysis on the counter data.

## The bot
`punc` is a python script that runs a continuous blocking call to Zulip and receives all messages posted to its subscribed streams. It counts certain tokens in every message it receives: certain punctuation marks, smileys, and ALL CAPS SENTENCES. It writes this information to a mongodb database.

## The app
the `punc` web app is a Flask application that reads from `punc`'s database and runs some analysis on the running count. It compares the relative frequency of each token in a stream to the overall average frequency of that stream, and then uses this information to describe the overall tenor of that stream.

![screenshot](https://www.dropbox.com/s/mybpc3ofgbd3a4e/Screenshot%202014-03-18%2017.23.31.png)

In other words, punc is data-driven journalism at its finest.