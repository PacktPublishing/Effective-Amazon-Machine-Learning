'''
Use this file to run a whole Amazon ML project:
- datasource creation
- model training
- evaluation

The main function is run_experiment


'''
import pandas as pd
import numpy as np
import json
import csv
import os

# ----------------------------------------------------------------------------
#  Initialization
#  Replace with your own paths and bucket
# ----------------------------------------------------------------------------

filepath = 'data/'
json_path = 'json/'
s3_path = 's3://aml.packt/data/'
s3_result_path = 's3://aml.packt/batch-prediction/result/'

# ----------------------------------------------------------------------------
#  Main function
#  run as:
#  run_experiment('my_experiment_001')
# ----------------------------------------------------------------------------


def run_experiment(experiment):
    '''
    This function is the main function
    It takes a string 'experiment' that drives the naming of the files

    - it generates the filenames for the datasources, schemas, recipes
    - it sends a randomized version of the data to an s3 bucket
    - creates the train, valid and test datasources
    - creates the model
    - creates the evaluation
    '''
    # start by generating all teh filenames for the current experiment
    filenames = generate_filenames(experiment)

    # load the data form local, shuffle and save back to original file
    df = pd.read_csv(filepath + filenames['main'])
    df = df.reindex(np.random.permutation(df.index))
    df.to_csv(filepath + filenames['main'], quoting= csv.QUOTE_NONNUMERIC, index=False)
    # sends the original file to s3
    os.system("aws s3 cp %s%s %s "% (filepath, filenames['main'], s3_path) )

    # write cli JSON
    create_dsrc("train", 0, 60)
    create_dsrc("valid", 60, 80)
    create_dsrc("test", 80, 100)

    create_model()
    create_eval("valid")
    create_eval("test")


# ----------------------------------------------------------------------------
#  datasource, model, evaluation and batch predictions functions
#  These functions all do the same thing
#  1. write the JSON parameters to a JSON formatted file in json_path folder
#  2. execute the AWS CLI command that will create the object: datasource, model, ...
# ----------------------------------------------------------------------------


def create_dsrc(mode, percentBegin, percentEnd):
    '''
    Input:
        mode: train, valid, or test
        percentBegin, percentEnd: dictate the slice of the original data used
                                for the  train, valid, or test subset
    * writes the datasource creation parameters in json format
      to {train|valid|test}_datasource.json
    * executes the cli command that creates the datasource
    '''
    # write the parameters in JSON format
    with open(json_path + "%s_datasource.json"%mode, 'w') as outfile:
        json.dump(json_dsrc(mode, percentBegin, percentEnd), outfile, indent=4)
    # create the datasource using the AWS CLI
    os.system("aws machinelearning create-data-source-from-s3 --cli-input-json file://%s%s_datasource.json"% (json_path, mode))

def create_model():
    '''
    * writes the model creation parameters in json format to generate_model.json
    * executes the cli command that creates the model
    '''
    # first write the parameters in JSON format
    with open(json_path + "generate_model.json", 'w') as outfile:
        json.dump(json_model(), outfile, indent=4)
    # create the model using the AWS CLI
    os.system("aws machinelearning create-ml-model --cli-input-json file://%sgenerate_model.json"% json_path)


def create_eval(mode = 'valid'):
    '''
    * writes the evaluation creation parameters in json format to generate_eval_{valid|test}.json
    * executes the cli command that creates the evaluation
    '''
    # first write the parameters in JSON format
    with open(json_path + "generate_eval_%s.json"% mode, 'w') as outfile:
        json.dump(json_eval(mode), outfile, indent=4)
    # create the evaluation using the AWS CLI
    os.system("aws machinelearning create-evaluation --cli-input-json file://%sgenerate_eval_%s.json"% (json_path, mode))

def create_prediction(mode = 'test'):
    '''
    * writes the batch-prediction creation parameters in json format to generate_prediction_{valid|test}.json
    * executes the cli command that creates the batch prediction
    '''
    # first write the parameters in JSON format
    with open(json_path + "generate_prediction_%s.json"% mode, 'w') as outfile:
        json.dump(json_prediction(mode), outfile, indent=4)
    # create the batch prediction using the AWS CLI
    os.system("aws machinelearning create-batch-prediction --cli-input-json file://%sgenerate_prediction_%s.json"% (json_path, mode))

# ----------------------------------------------------------------------------
#  datasource, model, evaluation and batch predictions parameters functions
#  These functions all return the parameter templates required to create
#  the AWS ML objects: datasource, model, evaluation and batch predictions
#  They use the filenames generated by the generate_filenames function
# ----------------------------------------------------------------------------

def json_dsrc(mode, percentBegin, percentEnd):
    '''
    datasource creation parameters
    '''
    return {
        "DataSourceId": "dsrc.ch6.ttnc_ext.%s.%s"% (mode, experiment),
        "DataSourceName": "DS Titanic %s [%s]"% (mode, experiment),
        "DataSpec": {
            "DataLocationS3": "%s%s"% (s3_path, filenames['main']),
            "DataSchemaLocationS3": "%s%s"% (s3_path, filenames['schema']),
            "DataRearrangement": "{\"splitting\":{\"percentBegin\":%s,\"percentEnd\":%s}}"% (percentBegin, percentEnd)
        },
        "ComputeStatistics": True
    }


def json_model():
    '''
    model creation parameters
    '''

    return {
        "MLModelId": "mdl.ch6.ttnc_ext.%s"% experiment,
        "MLModelName": "Model Titanic [%s]"% experiment,
        "MLModelType": "BINARY",
        "Parameters": {
            "sgd.maxPasses": "100",
            "sgd.shuffleType": "auto",
            "sgd.l2RegularizationAmount": "1.0E-06"
        },
        "TrainingDataSourceId": "dsrc.ch6.ttnc_ext.%s.%s"% ("train", experiment),
        "RecipeUri": "s3://aml.packt/data/no_qb_recipe.json"
    }

def json_eval(mode):
    '''
    evaluation creation parameters
    '''
    return {
        "EvaluationId": "eval.ch6.ttnc_ext.%s.%s"% (mode, experiment),
        "EvaluationName": "Eval Titanic %s [%s]"% (mode, experiment),
        "MLModelId": "mdl.ch6.ttnc_ext.%s"% experiment,
        "EvaluationDataSourceId": "dsrc.ch6.ttnc_ext.%s.%s"% (mode, experiment)
    }

def json_prediction(mode):
    '''
    batch prediction creation parameters
    '''
    return {
        "BatchPredictionId": "prd.ch6.ttnc_ext.%s.%s"% (mode,experiment),
        "BatchPredictionName": "Pred Titanic %s [%s]"% (mode,experiment),
        "MLModelId": "mdl.ch6.ttnc_ext.%s"% experiment,
        "BatchPredictionDataSourceId": "dsrc.ch6.ttnc_ext.%s.%s"% (mode, experiment),
        "OutputUri": "s3://aml.packt/"
    }

# ----------------------------------------------------------------------------
#  Getting the results
# ----------------------------------------------------------------------------

def get_batch_prediction(batch_prediction_id):
    '''
    This function uses the AWS CLI to return the results of the batch prediction
    given a batch_prediction_id
    '''
    command_str = "aws machinelearning get-batch-prediction --batch-prediction-id %s"% (batch_prediction_id)
    (output, err) = subprocess.Popen(command_str, stdout=subprocess.PIPE, shell=True).communicate()
    print(output.decode("utf-8"))
    print("aws s3 cp %sprd.ch6.ttnc_ext.%s.%s-%s.gz %s"% (s3_result_path,mode,experiment,filenames['main'], filepath) )
    return output.decode("utf-8")

def get_evaluation(evaluation_id):
    '''
    Given an evaluation ID, gets the evaluation results and extracts the AUC
    '''
    command_str = "aws machinelearning get-evaluation --evaluation-id %s"% evaluation_id
    (output, err) = subprocess.Popen(command_str, stdout=subprocess.PIPE, shell=True).communicate()
    res = json.loads( output.decode("utf-8"))
    auc = float(res['PerformanceMetrics']['Properties']['BinaryAUC'])
    print("%0.3f"%auc)
    return auc


def generate_filenames(experiment):
    '''
    takes a string 'experiment' as input and returns a JSON with
    the names of the files used for datasources, schema, and recipe
    main: filename of the file on your local
    train, valid and test: filenames for the different subsets
    schema: the schema file
    recipe: the recipe file
    '''
    return {
        'main': "ch6_original_titanic.csv",
        'train': "ch6_titanic.train.%s.csv"% experiment,
        'valid': "ch6_titanic.valid.%s.csv"% experiment,
        'test': "ch6_titanic.test.%s.csv"% experiment,
        'schema': "ch6_original_titanic.csv.schema",
        'recipe': "default_recipe.json",
    }

# ----------------------------------------------------------------------------
#  Running experiments
# ----------------------------------------------------------------------------

# Memorize the results in a list
results = []
n_experiment = 5
# Run 5 experiments and capture the AUC
for n in range(n_experiment):
    run_experiment('default_0%s'%n)
    auc = get_evaluation("eval.ch6.ttnc_orig.valid.default_0%s"%n)
    results.append(auc)
