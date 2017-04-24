from lib.tweets import ATweets

import json
import boto3
from textblob import TextBlob

import base64


# stream_name = "veggieStream"
stream_name = "veggieLambda"

# search_query = 'brocolli OR carrot OR artichoke OR lentils OR spinach'
firehose = boto3.client('firehose')
k = 0

vegetables = ['artichoke','asparagus', 'avocado', 'brocolli','cabbage', 'carrot', 'cauliflower','celery', 'chickpea', 'corn','cucumber', 'eggplant','endive', 'garlic', 'green beans', 'kale', 'leek', 'lentils', 'lettuce','mushroom','okra', 'onion','parsnip', 'potato','pumpkin', 'radish','turnip', 'quinoa', 'rice', 'spinach', 'squash' , 'tomato', 'yams', 'zuchinni']
# vegetables = ['artichoke','asparagus', 'carrot',  'corn']

for veggie in vegetables:
    raw_query   = 'f=tweets&vertical=default&l=en&q={0}&src=typd'.format(veggie)

    tw = ATweets(raw_query)
    statuses = tw.capture()

    for st in statuses:
        k +=1

        if (st.lang=='en') & (st.retweeted_status is None) & (len(st.text) > 10):
            tb = TextBlob(st.text)
            tb_polarity = str(tb.sentiment.polarity)

            # clean_tweet = ''.join([s for s in st.text if s not in [',', '\n', '.', '#','|', ';', '"']])
            clean_tweet = ''.join([s for s in st.text if s not in [',', '\n']])
            record = ','.join([str(st.id), st.user.screen_name,veggie, tb_polarity,  clean_tweet]) + '\n'
            # record_b64 = base64.b64encode(record)
            response = firehose.put_record( DeliveryStreamName = stream_name, Record={'Data': record} )
            print("\n=={2}==={1} \n{0}".format(record, k, veggie))


print("Status length: {0}".format(k))

# { 'screen_name': st.user.screen_name, 'text' : st.text, 'lang': st.lang, 'source': st.source }
