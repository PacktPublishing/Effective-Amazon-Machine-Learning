# -----------------------------------------------------------------------------
#  Python scripts for chapter 7
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#  Boto3 the Python SDK
# -----------------------------------------------------------------------------



pip install boto3

import boto3
# Initialize the S3 client
s3 = boto3.resource('s3')
# List all the buckets in out account
for bucket in s3.buckets.all():
    print(bucket.name)

# -----------------------------------------------------------------------------
# load the file
data = open('data/ames_housing_nohead.csv', 'rb')
s3.Object('aml.packt', 'data/ames_housing_nohead.csv').put(Body=data)

# -----------------------------------------------------------------------------
#  Working with the Python SDK for Amazon Machine Learning
# -----------------------------------------------------------------------------

def name_id_generation(prefix, mode, trial):
    Id = '_'.join([prefix, mode, "%02d"%int(trial)])
    name = "[%s] %s %02d"% (prefix, mode, int(trial) )
    return {'Name':name, 'Id':Id}

# -----------------------------------------------------------------------------

# The iteration number of our experiements
trial = 5
# The S3 location of schemas and files
data_s3   = 's3://aml.packt/data/ch8/ames_housing_shuffled.csv'
schema_s3 = 's3://aml.packt/data/ch8/ames_housing.csv.schema'
recipe_s3 = 's3://aml.packt/data/ch8/recipe_ames_housing_001.json'

# And the parameters for the SGD algrithm
sgd_params = {
  "sgd.shuffleType": "auto",
  "sgd.l1RegularizationAmount": "1.0E-04",
  "sgd.maxPasses": "100"
}


# -----------------------------------------------------------------------------
import boto3
import time
import json

# -----------------------------------------------------------------------------
client = boto3.client('machinelearning')


# -----------------------------------------------------------------------------
# Create datasource for training
resource = name_id_generation('DS', 'training', trial)
print("Creating datasources for training (%s)"% resource['Name'] )
response = client.create_data_source_from_s3(
  DataSourceId = resource['Id'] ,
  DataSourceName = resource['Name'],
  DataSpec = {
    'DataLocationS3' : data_s3,
    'DataSchemaLocationS3' : schema_s3,
   'DataRearrangement':'{"splitting":{"percentBegin":0,"percentEnd":70}}'
  },
   ComputeStatistics = True
)

# Create datasource for validation
resource = name_id_generation('DS', 'validation', trial)
print("Creating datasources for validation (%s)"% resource['Name'] )
response = client.create_data_source_from_s3(
  DataSourceId = resource['Id'] ,
  DataSourceName = resource['Name'],
  DataSpec = {
    'DataLocationS3': data_s3,
    'DataSchemaLocationS3': schema_s3,
    'DataRearrangement':'{"splitting":{"percentBegin":0,"percentEnd":70}}'
  },
  ComputeStatistics = True
)

# -----------------------------------------------------------------------------
# Train model with existing recipe
resource = name_id_generation('MDL', '', trial)
print("Training model (%s) with params:n%s"%
               (resource['Name'], json.dumps(sgd_params, indent=4)) )
response = client.create_ml_model(
  MLModelId = resource['Id'],
  MLModelName = resource['Name'],
  MLModelType = 'REGRESSION',
  Parameters = sgd_params,
  TrainingDataSourceId= name_id_generation('DS', 'training', trial)['Id'],
  RecipeUri = recipe_s3
)


# -----------------------------------------------------------------------------
resource = name_id_generation('EVAL', '', trial)
print("Launching evaluation (%s) "% resource['Name'] )
response = client.create_evaluation(
  EvaluationId = resource['Id'],
  EvaluationName = resource['Name'],
  MLModelId = name_id_generation('MDL', '', trial)['Id'],
  EvaluationDataSourceId = name_id_generation('DS', 'validation', trial)
  ['Id']
)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#  Waiting on operation completion
# -----------------------------------------------------------------------------

waiter = client.get_waiter('evaluation_available')

# -----------------------------------------------------------------------------

waiter.wait(FilterVariable='Name', EQ='the name of the evaluation')

# -----------------------------------------------------------------------------

waiter.wait(FilterVariable='DataSourceId', EQ='the DatasourceId')

# -----------------------------------------------------------------------------

t0 = time.time()
# declare the waiter and call the wait method on the evaluation
waiter = client.get_waiter('evaluation_available')
print("Waiting on evaluation to finish ")
waiter.wait(FilterVariable='Name',
            EQ=name_id_generation('EVAL', '', trial)['Name'])
t = time.time() - t0
print("Evaluation has finished after %sm %ss"% (int(t/60), t%60) )
# get the evaluation results
response = client.get_evaluation(
  EvaluationId=name_id_generation('EVAL', '', trial)['Id']
)
RMSE =float(response['PerformanceMetrics']['Properties']['RegressionRMSE'])
print("[trial %0.2f] RMSE %0.2f"% (trial, RMSE) )
# and delete the resources
print("Deleting datasources and model")
response = client.delete_data_source(
  DataSourceId=name_id_generation('DS', 'training', trial)['Id']
)
response = client.delete_data_source(
  DataSourceId=name_id_generation('DS', 'validation', trial)['Id']
)
response = client.delete_ml_model(
  MLModelId=name_id_generation('MDL', '', trial)['Id']
)

# -----------------------------------------------------------------------------

Creating datasources for training ([DS] training 04)
Creating datasources for validation ([DS] validation 04)
Training model ([MDL] 04) with params:
{
  "sgd.shuffleType": "auto",
  "sgd.l1RegularizationAmount": "1.0E-04",
  "sgd.maxPasses": "100"
}
Launching evaluation ([EVAL] 04)
Waiting on evaluation to finish
Evaluation has finished after 11m 43.78s
[trial 4] RMSE 22437.33
Deleting datasources and model


# -----------------------------------------------------------------------------
#  Managing schema and recipe
# -----------------------------------------------------------------------------

import pandas as pd
import boto3
import json

# Local schema with all the features
original_schema_filename = 'data/ames_housing.csv.schema'
# Initialize boto3 objects
s3 = boto3.resource('s3')
client = boto3.client('machinelearning')

# load dataset and feature_ names
df = pd.read_csv('data/ames_housing.csv')
original_features = df.columns.difference(['SalePrice', 'Order'])

# load original schema with all the features
schema = json.load( open(original_schema_filename) )

# SGD parameters: L1 heavy regularization
sgd_parameters = {
  "sgd.shuffleType": "auto",
  "sgd.l1RegularizationAmount": "1.0E-04",
  "sgd.maxPasses": "100"
}

# memorize all object Ids for future deletion
baseline_rmse = 61507.35
datasource_ids = []
model_ids = []
evaluation_ids = []
features_rmse = {}

def generate_trial(n):
    n = "X" + str(n).zfill(3)
    return {
        'schema_filename': "rfs_ames_housing_%s.schema"% n,
        'recipe_s3': 's3://aml.packt/RFS/recipe_ames_housing_default.json',
        'data_s3': 's3://aml.packt/RFS/ames_housing_shuffled.csv',
        'datasource_training_id': "rfs_training_%s"% n,
        'datasource_training_name': "[DS RFS] training %s"% n,
        'datasource_validation_id': "rfs_validation_%s"% n,
        'datasource_validation_name': "[DS RFS] validation %s"% n,
        'model_id': "rfs_%s"% n,
        'model_name': "[MDL RFS] %s"% n,
        'evaluation_id': "rfs_%s"% n,
        'evaluation_name': "[EVAL RFS] %s"% n,
    }

# -----------------------------------------------------------------------------
for k in range(10):
    print("="* 10 + " feature: %s"% original_features[k])
    trial = generate_trial(k)

    # remove feature[k] from schema and upload to S3
    schema['excludedAttributeNames'] = [original_features[k]]
    with open("data/%s"%trial['schema_filename'], 'w') as fp:
        json.dump(schema, fp, indent=4)
        s3.Object('aml.packt', "RFS/%s"% trial['schema_filename']).put(
                            Body=open("data/%s"%trial['schema_filename'], 'rb')
                        )

    # create datasource
    print("Datasource %s"% trial['datasource_training_name'])
    datasource_ids.append( trial['datasource_training_id'] )
    response = client.create_data_source_from_s3(
        DataSourceId = trial['datasource_training_id'] ,
        DataSourceName= trial['datasource_training_name'] ,
        DataSpec={
            'DataLocationS3': trial['data_s3'],
            'DataRearrangement': '{                                 \
                "splitting": {"percentBegin":0,"percentEnd":70}}',
                'DataSchemaLocationS3': "s3://aml.packt/RFS/%s"%    \
                        trial['schema_filename']
            },
        ComputeStatistics=True
    )

    # Create datasource for validation
    print("Datasource %s"% trial['datasource_validation_name'])
    datasource_ids.append( trial['datasource_validation_id'] )
    response = client.create_data_source_from_s3(
        DataSourceId = trial['datasource_validation_id'] ,
        DataSourceName= trial['datasource_validation_name'] ,
        DataSpec={
            'DataLocationS3': trial['data_s3'],
            'DataRearrangement': '{                                   \
                "splitting": {"percentBegin":70,"percentEnd":100}}',
            'DataSchemaLocationS3': "s3://aml.packt/RFS/%s"%          \
                        trial['schema_filename']
        },
        ComputeStatistics=True
    )

    # Train model with existing recipe
    print("Model %s"% trial['model_name'])
    model_ids.append(trial['model_id'] )
    response = client.create_ml_model(
        MLModelId = trial['model_id'],
        MLModelName = trial['model_name'],
        MLModelType = 'REGRESSION',
        Parameters = sgd_parameters,
        TrainingDataSourceId = trial['datasource_training_id'] ,
        RecipeUri = trial['recipe_s3']
    )

    print("Evaluation %s"% trial['evaluation_name'])
    evaluation_ids.append(trial['evaluation_id'])
    response = client.create_evaluation(
        EvaluationId = trial['evaluation_id'],
        EvaluationName = trial['evaluation_name'],
        MLModelId = trial['model_id'],
        EvaluationDataSourceId= trial['datasource_validation_id']
    )


# -----------------------------------------------------------------------------
for k in range(10):
    trial = generate_trial(k)
    waiter = client.get_waiter('evaluation_available')
    print("Waiting on evaluation %s to finish "% trial['evaluation_name'])
    waiter.wait(FilterVariable='Name', EQ=trial['evaluation_name'])
    print("Evaluation has finished ")

    response = client.get_evaluation( EvaluationId=trial['evaluation_id'] )
    features_rmse[original_features[k]] = float(
                response['PerformanceMetrics']['Properties']['RegressionRMSE']
            )
    print("[%s] RMSE %0.2f"% (
        original_features[k],
        float(response['PerformanceMetrics']['Properties']['RegressionRMSE']))
    )
    # Now delete the resources
    print("Deleting datasources and model")
    response = client.delete_data_source(
        DataSourceId = trial['datasource_training_id']
    )
    response = client.delete_data_source(
        DataSourceId = trial['datasource_validation_id']
    )
    response = client.delete_ml_model(
        MLModelId = trial['model_id']
    )

print("removing the feature increased the RMSE by ")
for k,v in features_rmse.items():
    print("%s t%0.2f %% "% (k, (baseline_rmse - v)/ baseline_rmse *100.0 ) )

# -----------------------------------------------------------------------------



