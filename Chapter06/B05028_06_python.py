# -----------------------------------------------------------------------------
#  Python code for chapter 6
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#  Calculate ROC AUC
# -----------------------------------------------------------------------------
import pandas as pd
from sklearn import metrics

# open file the csv file on your local
df = pd.read_csv(path/location_of_the_unzipped_results_csv _file)

# calculate the true and false positive rate
fpr, tpr, threshold = metrics.roc_curve(df.trueLabel, df.score)
# Calculate ROC_AUC
roc_auc = metrics.auc(fpr, tpr)


# -----------------------------------------------------------------------------
#  Boto3 intialize client machine learning
# -----------------------------------------------------------------------------
import boto3

# Initialize the client
client = boto3.client('machinelearning')

# -----------------------------------------------------------------------------
#  Real time endpoint
# -----------------------------------------------------------------------------

import boto3
import json  # for parsing the returned predictions

# Initialize the client
client = boto3.client('machinelearning')

# The endpoint url is obtained from the model summary
endpoint_url = "https://realtime.machinelearning.us-east-1.amazonaws.com/"

# Replace with your own model ID
model_id = "ml-kJmiRxxxxxx"

# The actual sample to be predicted. JSON formatted
record = { "nature": "Hello world, my name is Alex" }

# Predict the classification
response = client.predict(
   MLModelId       = model_id,
   Record          = record,
   PredictEndpoint = endpoint_url
)

# Print the results
print(json.dumps(response, indent=4))

# -----------------------------------------------------------------------------
#  Output JSON
# -----------------------------------------------------------------------------

{
   "ResponseMetadata": {
       "RetryAttempts": 0,
       "HTTPHeaders": {
           "content-type": "application/x-amz-json-1.1",
           "content-length": "143",
           "date": "Tue, 10 Jan 2017 16:20:49 GMT",
           "x-amzn-requestid": "bfab2af0-d750-11e6-b8c2-45ac3ab2f186"
       },
       "HTTPStatusCode": 200,
       "RequestId": "bfab2af0-d750-11e6-b8c2-45ac3ab2f186"
   },
   "Prediction": {
       "predictedScores": {
           "0": 0.001197131467051804
       },
       "predictedLabel": "0",
       "details": {
           "PredictiveModelType": "BINARY",
           "Algorithm": "SGD"
       }
   }
}

# -----------------------------------------------------------------------------
#  Send several samples to real time endpoint
# -----------------------------------------------------------------------------

import boto3
import json
import pandas as pd

# Initialize the Service, the Model ID and the endpoint url
client = boto3.client('machinelearning')
# replace with your own endpoint url and model ID
endpoint_url = "https://realtime.machinelearning.us-east-1.amazonaws.com"
model_id = "ml-kJmiRHyn1UM"

# Memorize which class is spam and which is ham
spam_label = {'0': 'ham', '1':'spam'}

# Load the held out dataset into a panda DataFrame
df = pd.read_csv('held-out.csv')

# Loop over each DataFrame rows
for index, row in df.iterrows():
   # The record
   record = { "body": row['sms'] }
   response = client.predict(
       MLModelId       = model_id,
       Record          = record,
       PredictEndpoint = endpoint_url
   )

   # get the label and score from the response
   predicted_label = response['Prediction']['predictedLabel']
   predicted_score = response['Prediction']['predictedScores'][predicted_label]
   print("[%s] %s (%0.2f):t %s "% (spam_label[str(row['nature'])],
                               spam_label[predicted_label],
                               predicted_score,
                               row['sms'] )
   )


