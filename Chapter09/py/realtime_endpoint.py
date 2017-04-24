import boto3
client = boto3.client('machinelearning')

response = client.predict(
    MLModelId = "ml-ZHqxUjPNQTq",
    Record = { "SentimentText": "Hello world, this is a sad day" },
    PredictEndpoint = "https://realtime.machinelearning.us-east-1.amazonaws.com"
)



import boto3
ml_client = boto3.client('machinelearning')

response = ml_client.predict(
    MLModelId = "ml-ZHqxUjPNQTq",
    Record = { "SentimentText": tw },
    PredictEndpoint = "https://realtime.machinelearning.us-east-1.amazonaws.com"
)



