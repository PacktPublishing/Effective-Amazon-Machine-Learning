'''
The implements feature selection on Amazon ML
'''
import pandas as pd
import boto3
import json

original_schema_filename = 'data/ames_housing.csv.schema'

s3_client   = boto3.resource('s3')
ml_client   = boto3.client('machinelearning')

# load dataset and feature_ names
df = pd.read_csv('data/ames_housing.csv')
# list all features keeping 'SalePrice', 'Order'
original_features = df.columns.difference(['SalePrice', 'Order'])

# load schema
schema = json.load( open(original_schema_filename) )

# SGD parameters
sgd_parameters = {
    "sgd.shuffleType": "auto",
    "sgd.l1RegularizationAmount": "1.0E-04",
    "sgd.maxPasses": "100"
}

# Memorize all object Ids for future deletion
baseline_rmse   = 61507.35
datasource_ids  = []
model_ids       = []
evaluation_ids  = []
features_rmse   = {}

def generate_trial(n):
    '''
    This function returns all the filenames, object names and IDs necessary for a run
    '''
    identifier = "X" + str(n).zfill(3)
    return {
        'schema_filename':  "rfs_ames_housing_%s.schema"% identifier,
        'recipe_s3':        's3://aml.packt/RFS/recipe_ames_housing_default.json',
        'data_s3':          's3://aml.packt/RFS/ames_housing_shuffled.csv',
        'datasource_training_id':   "rfs_training_%s"% identifier,
        'datasource_training_name': "[DS RFS] training %s"% identifier,
        'datasource_validation_id':   "rfs_validation_%s"% identifier,
        'datasource_validation_name': "[DS RFS] validation %s"% identifier,
        'model_id':   "rfs_%s"% identifier,
        'model_name': "[MDL RFS] %s"% identifier,
        'evaluation_id':   "rfs_%s"% identifier,
        'evaluation_name': "[EVAL RFS] %s"% identifier,
    }

# ------------------------------------------------------------------------------
#  Runs 10 model training and evaluation each time
#  removing a different feature: original_features[k]
# ------------------------------------------------------------------------------
for k in range(10):
    print("="* 10 + " feature: %s"% original_features[k])
    trial = generate_trial(k)

    # remove feature[k] from schema and upload to S3
    schema['excludedAttributeNames'] = [original_features[k]]
    with open("data/%s"%trial['schema_filename'], 'w') as fp:
        json.dump(schema, fp, indent=4)
    s3_client.Object('aml.packt', "RFS/%s"% trial['schema_filename']).put(Body=open("data/%s"%trial['schema_filename'], 'rb'))

    # create datasource
    print("Datasource %s"% trial['datasource_training_name'])
    datasource_ids.append( trial['datasource_training_id']  )
    response = ml_client.create_data_source_from_s3(
        DataSourceId  = trial['datasource_training_id'] ,
        DataSourceName= trial['datasource_training_name'] ,
        DataSpec={
            'DataLocationS3': trial['data_s3'],
            'DataRearrangement': '{\"splitting\":{\"percentBegin\":0,\"percentEnd\":70}}',
            'DataSchemaLocationS3': "s3://aml.packt/RFS/%s"% trial['schema_filename']
        },
        ComputeStatistics=True
    )

    # Create datasource for validation
    print("Datasource %s"% trial['datasource_validation_name'])
    datasource_ids.append( trial['datasource_validation_id']  )
    response = ml_client.create_data_source_from_s3(
        DataSourceId  = trial['datasource_validation_id'] ,
        DataSourceName= trial['datasource_validation_name'] ,
        DataSpec={
            'DataLocationS3': trial['data_s3'],
            'DataRearrangement': '{\"splitting\":{\"percentBegin\":70,\"percentEnd\":100}}',
            'DataSchemaLocationS3': "s3://aml.packt/RFS/%s"% trial['schema_filename']
        },
        ComputeStatistics=True
    )

    # Train model with existing recipe
    print("Model %s"% trial['model_name'])
    model_ids.append(trial['model_id']  )
    response = ml_client.create_ml_model(
        MLModelId   = trial['model_id'],
        MLModelName = trial['model_name'],
        MLModelType = 'REGRESSION',
        Parameters  = sgd_parameters,
        TrainingDataSourceId = trial['datasource_training_id'] ,
        RecipeUri   = trial['recipe_s3']
    )

    print("Evaluation %s"% trial['evaluation_name'])
    evaluation_ids.append(trial['evaluation_id'])
    response = ml_client.create_evaluation(
        EvaluationId    = trial['evaluation_id'],
        EvaluationName  = trial['evaluation_name'],
        MLModelId       = trial['model_id'],
        EvaluationDataSourceId= trial['datasource_validation_id']
    )

# get results and delete resources

for k in range(10):
    trial = generate_trial(k)
    waiter = ml_client.get_waiter('evaluation_available')
    print("Waiting on evaluation %s to finish "% trial['evaluation_name'])
    waiter.wait(FilterVariable='Name', EQ=trial['evaluation_name'])
    print("Evaluation has finished ")

    response = ml_client.get_evaluation( EvaluationId=trial['evaluation_id'] )
    features_rmse[original_features[k]] = float(response['PerformanceMetrics']['Properties']['RegressionRMSE'])
    print("[%s] RMSE %0.2f"% (original_features[k], float(response['PerformanceMetrics']['Properties']['RegressionRMSE'])) )
    # Now delete the resources
    print("Deleting datasources and model")
    response = ml_client.delete_data_source(
        DataSourceId = trial['datasource_training_id']
    )
    response = ml_client.delete_data_source(
        DataSourceId = trial['datasource_validation_id']
    )
    response = ml_client.delete_ml_model(
        MLModelId = trial['model_id']
    )

print("removing the feature increased the RMSE by ")
for k,v in features_rmse.items():
    print("%s \t%0.2f %%  "%  (k,  (baseline_rmse - v)/ baseline_rmse *100.0   )  )


