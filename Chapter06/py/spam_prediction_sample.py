# ---------------------------------------------------------------------------------
#  1. single text sample: spam prediction
# ---------------------------------------------------------------------------------


import boto3
import json
import pandas as pd

# Define the service
client = boto3.client('machinelearning')

# Realtime prediction endpoint url given in the model summary
endpoint_url = "https://realtime.machinelearning.us-east-1.amazonaws.com"

# Model id to be used, replace with your model ID
model_id = "ml-kJmiRHyn1UM"

# Actual text samples to be predicted. JSON formatted
# The first one should not be classfified as spam while the second should

record = {
        "body": "Hello world, my name is Alex"
    }

record = {
        "body": "Call now to get free contacts for free, no cash no credit card."
    }

# Use the predict() method of the machine learning service
response = client.predict(
    MLModelId       = model_id,
    Record          = record,
    PredictEndpoint = endpoint_url
)

print(json.dumps(response, indent=4))

# ---------------------------------------------------------------------------------
#  2. Prediction on the heldout dataset
#     calculate and plot ROC-AUC
# ---------------------------------------------------------------------------------


import boto3
import json
import pandas as pd
from sklearn import metrics

# file with heldout spam dataset
filename = "ch6/data/spam_heldout.csv"

# Initialize the Service, the Model ID and the endpoint url
client = boto3.client('machinelearning')
endpoint_url = "https://realtime.machinelearning.us-east-1.amazonaws.com"
# Replace with your model ID
model_id = "ml-kJmiRHyn1UM"

# Recall which class is spam and which is ham
spam_label = {'0': 'ham', '1':'spam'}

# Load the held out dataset into a panda DataFrame
df = pd.read_csv(filename)
df['predicted'] = -1
df['predicted_score'] = -1

# Loop over each DataFrame rows
for index, row in df.iterrows():
    record = { "body": row['sms'] }
    response = client.predict(
        MLModelId       = model_id,
        Record          = record,
        PredictEndpoint = endpoint_url
    )
    predicted_label = response['Prediction']['predictedLabel']
    predicted_score = response['Prediction']['predictedScores'][predicted_label]
    print("[%s] %s (%0.2f):\t %s "% (spam_label[str(row['nature'])],
                                spam_label[predicted_label],
                                predicted_score,
                                row['sms'] )
    )

    df.loc[index, 'predicted'] = int(response['Prediction']['predictedLabel'])
    df.loc[index, 'predicted'] = int(predicted_label)
    df.loc[index, 'predicted_score'] = predicted_score

# Calculate ROC-AUC

fpr, tpr, threshold = metrics.roc_curve(df.nature, df.predicted_score)
roc_auc = metrics.auc(fpr, tpr)

# Plot ROC curve

import matplotlib.pyplot as plt
%matplotlib


fig, ax = plt.subplots(1,1, figsize=(8,8))

ax.set_axis_bgcolor('white')
ax.set_title('ROC - Spam dataset')
ax.grid()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlabel('True Positive Rate')
ax.set_ylabel('False Positive Rate')

ax.plot(fpr, tpr, 'b', label='AUC = %0.2f' % roc_auc)
ax.plot([0, 1], [0, 1],'r--')

ax.legend(loc='lower right')
ax.set_xlim(-0.05, 1.)
ax.set_ylim(0, 1.05)
plt.tight_layout()
plt.show()



