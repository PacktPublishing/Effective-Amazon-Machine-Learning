from __future__ import print_function

import base64
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ml_client = boto3.client('machinelearning')

print('Loading function')

def get_sentiment(payload):
    payload = payload.split(',')
    tweet = payload.pop(4)

    response = ml_client.predict(
        MLModelId = "ml-ZHqxUjPNQTq",
        Record = { "SentimentText": tweet },
        PredictEndpoint = "https://realtime.machinelearning.us-east-1.amazonaws.com"
    )
    logger.info('-- response {0}'.format(response) )
    predicted_label = response['Prediction']['predictedLabel']
    predicted_score = response['Prediction']['predictedScores'][predicted_label]

    logger.info('-- predicted_label {0}'.format(predicted_label) )
    logger.info('-- predicted_score {0}'.format(predicted_score) )

    return predicted_label, predicted_score


def lambda_handler(event, context):
    output = []
    logger.info('in the handler')

    for record in event['records']:
        print(record['recordId'])
        logger.info('record_id {0}'.format(record['recordId']))
        payload = base64.b64decode(record['data'])
        predicted_label, predicted_score = get_sentiment(payload)
        logger.info('--R predicted_label {0}'.format(predicted_label) )
        logger.info('--R predicted_score {0}'.format(predicted_score) )

        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(payload)
        }
        logger.info('output_record {0}'.format(output_record))
        output.append(output_record)

    logger.info('Successfully processed {} records.'.format(len(event['records'])))
    print('Successfully processed {} records.'.format(len(event['records'])))

    return {'records': output}

