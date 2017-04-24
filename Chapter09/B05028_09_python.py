# -----------------------------------------------------------------------------
#  Python scripts for chapter 9
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#  The training dataset and the model
# -----------------------------------------------------------------------------

import boto3
client = boto3.client('machinelearning')
client.predict(
   MLModelId = "ml-ZHqxUjPNQTq",
   Record = { "SentimentText": "Hello world, this is a great day" },
   PredictEndpoint = "https://realtime.machinelearning.us-east-1.amazonaws.com"
)

# -----------------------------------------------------------------------------
#  Producing tweets
# -----------------------------------------------------------------------------


import twitter
class ATweets():
    def __init__(self, raw_query):
        self.twitter_api = twitter.Api(consumer_key='your own key',
            consumer_secret= 'your own key',
            access_token_key='your own key',
            access_token_secret='your own key')
        self.raw_query = raw_query

    # capture the tweets:
    # see http://python-twitter.readthedocs.io/en/latest/twitter.html
    def capture(self):
        statuses = self.twitter_api.GetSearch(
            raw_query = self.raw_query,
            lang = 'en',
            count=100, result_type='recent', include_entities=True
        )
     return statuses
# -----------------------------------------------------------------------------
tw = ATweets(raw_query)
statuses = tw.capture()

# -----------------------------------------------------------------------------
from tweets import ATweets
import json
import boto3

# The kinesis firehose delivery stream we send data to
stream_name = "veggieTweets"

# Initialize the firehose client
firehose = boto3.client('firehose')

# Our own homemade list of vegetables, feel free to add seasoning
vegetables = ['artichoke','asparagus', 'avocado', 'brocolli','cabbage','carrot',
    'cauliflower','celery', 'chickpea', 'corn','cucumber', 'eggplant','endive',
    'garlic', 'green beans', 'kale', 'leek', 'lentils', 'lettuce','mushroom',
    'okra', 'onion','parsnip', 'potato','pumpkin', 'radish','turnip', 'quinoa',
    'rice', 'spinach', 'squash' , 'tomato', 'yams', 'zuchinni']

# Loop over all vegetables
for veggie in vegetables:
    # for a given veggie define the query and capture the tweets
    raw_query = 'f=tweets&vertical=default&l=en&q={0}&src=typd'.format(veggie)
    # capture the tweets
    tw = ATweets(raw_query)
    statuses = tw.capture()
    # and for each tweet, cleanup, add other data and send to firehose
    for status in statuses:
        # remove commas and line returns from tweets
        clean_tweet = ''.join([s for s in st.text if s not in [',', 'n']])
        # and build the record to be sent as a comma separated string
        # followed by a line return
        record=(','.join([str(st.id),st.user.screen_name,veggie, clean_tweet])
                    + 'n')
        # send the record to firehose
        response=firehose.put_record(DeliveryStreamName = stream_name,
                                    Record={'Data': record} )


# -----------------------------------------------------------------------------
(st.lang=='en') & (st.retweeted_status is None) & (len(st.text) > 10):

# -----------------------------------------------------------------------------
#  Preprocessing with Lambda
# -----------------------------------------------------------------------------

from __future__ import print_function

import base64
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ml_client = boto3.client('machinelearning')

print('Loading function')

def lambda_handler(event, context):
    output = []
    for record in event['records']:
        payload = base64.b64decode(record['data'])
        payload = payload.split(',')
        tweet = payload.pop(4)

        predicted_label, predicted_score = get_sentiment(tweet)

        payload.append(str(predicted_label) )
        payload.append(str(predicted_score) )
        payload.append(tweet)
        payload = ','.join(payload)

        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(payload)
        }
        output.append(output_record)
        return {'records': output}

# -----------------------------------------------------------------------------
def get_sentiment(tweet):

    response = ml_client.predict(
        MLModelId = "ml-ZHqxUjPNQTq",
        Record = { "SentimentText": tweet },
        PredictEndpoint="https://realtime.machinelearning.us-east-1.amazonaws.com"
    )
    predicted_label = response['Prediction']['predictedLabel']
    predicted_score = response['Prediction']['predictedScores'][predicted_label]

    return predicted_label, predicted_score


# -----------------------------------------------------------------------------
#  Download the dataset from RedShift
# -----------------------------------------------------------------------------

import pandas as pd
df = pd.read_csv('data/veggie_tweets.csv')

# -----------------------------------------------------------------------------
#  Sentiment analysis with TextBlob
# -----------------------------------------------------------------------------

from textblob import TextBlob
print(TextBlob(text).sentiment)


# -----------------------------------------------------------------------------
from textblob import TextBlob
df['tb_polarity'] = 0
for i, row in df.iterrows():
    df.loc[i, 'tb_polarity'] = TextBlob(row['text']).sentiment.polarity

# -----------------------------------------------------------------------------
#  Removing duplicate tweets
# -----------------------------------------------------------------------------
' '.join([token for token tk in tweet.split(' ') if 'https://t.co/' not in tk])

# -----------------------------------------------------------------------------
df['new_column'] = df[existing_column].apply(
                    lambda existing_column : {
                        some operation or function on existing_column
                    }
                )

# -----------------------------------------------------------------------------
df['no_urls'] = df['text'].apply(
                   lambda tweet : ' '.join(
                       [tk for  tk in tweet.split(' ')
                        if 'https://t.co/' not in tk]
                   )
                )

# -----------------------------------------------------------------------------
df.drop_duplicates(subset= ['no_urls'], inplace = True)

