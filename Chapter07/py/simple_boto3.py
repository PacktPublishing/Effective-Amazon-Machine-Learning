'''
This script shows a simple straightforward Amazon ML project
- 2 data sources are created from S3: training and validation
- a model is trained
- an evaluation is carried out
- the results are retrieved

Adapt the location of the following files to your own environment:
* The dataset is located on s3://aml.packt/data/ch7/ames_housing.csv
* The schema is at s3://aml.packt/data/ch7/ames_housing.csv.schema
* The recipe is at s3://aml.packt/data/ch7/recipe_ames_housing_001.json

'''

import boto3

# define the service you want to interact with
client = boto3.client('machinelearning')

# Create datasource for training
response = client.create_data_source_from_s3(
    DataSourceId='bt3_training_001',
    DataSourceName='[DS] training 001',
    DataSpec={
        'DataLocationS3': 's3://aml.packt/data/ch7/ames_housing.csv',
        'DataRearrangement': '{\"splitting\":{\"percentBegin\":0,\"percentEnd\":70}}',
        'DataSchemaLocationS3': 's3://aml.packt/data/ch7/ames_housing.csv.schema'
    },
    ComputeStatistics=True
)

# Create datasource for validation
response = client.create_data_source_from_s3(
    DataSourceId='bt3_validation_001',
    DataSourceName='[DS] validation 001',
    DataSpec={
        'DataLocationS3': 's3://aml.packt/data/ch7/ames_housing.csv',
        'DataRearrangement': '{\"splitting\":{\"percentBegin\":70,\"percentEnd\":100}}',
        'DataSchemaLocationS3': 's3://aml.packt/data/ch7/ames_housing.csv.schema'
    },
    ComputeStatistics=True
)

# Train model with existing recipe
response = client.create_ml_model(
    MLModelId='bt3_001',
    MLModelName='[MDL] 001',
    MLModelType='REGRESSION',
    Parameters={
        "sgd.shuffleType": "auto",
        "sgd.l1RegularizationAmount": "1.0E-04",
        "sgd.maxPasses": "100"
    },
    TrainingDataSourceId='bt3_training_001',
    RecipeUri='s3://aml.packt/data/ch7/recipe_ames_housing_001.json'
)

# Create evaluation
response = client.create_evaluation(
    EvaluationId='bt3_001',
    EvaluationName='[EVAL] 001',
    MLModelId='bt3_001',
    EvaluationDataSourceId='bt3_validation_001'
)

# Get evaluation result
response = client.get_evaluation(
    EvaluationId='bt3_001'
)
