'''
Runs several trials on the non linear dataset with Montecarlo cross validation

Assuming
* the data is in a Redshift database with 2 columns: x and y.
* schema is available on s3
* recipe is available on s3: no transformation

for each power:
    3 times
        Create training and evaluation datasource
        create model
        evaluate model
        get results
    average result

nl = NonLinear(5, 5, 'noqb_aml')
nl.run_all_trials()
nl.get_results()

nl.run_trial(0,2,'alpha')
nl.create_datasource(0, 'training', 2)

'''

import pandas as pd
import boto3
import json
import csv

class NonLinear():

    def __init__(self, max_p, n_crossval, prefix):
        self.trials = []
        self.max_p  = max_p
        self.n_crossval = n_crossval
        self.prefix = prefix
        self.client = boto3.client('machinelearning')
        self.sgd_parameters = {
            "sgd.shuffleType": "auto",
            "sgd.l2RegularizationAmount": "1.0E-06",
            "sgd.maxPasses": "100"
        }

        self.recipe = {
            "groups" : {},
            "assignments" : { },
            "outputs": ["ALL_INPUTS"]
            # "outputs": ["quantile_bin(ALL_NUMERIC,200)"]
        }

    def run_all_trials(self):
        for p in range(1,self.max_p+1):
            for k in range(self.n_crossval):
                self.trials.append( self.run_trial(p,k) )

    def run_trial(self, p, k ):
        self.ds_training    = self.create_datasource(p, k, 'training')
        self.ds_evaluation  = self.create_datasource(p, k, 'evaluation')
        self.model          = self.create_model(p,k)
        self.evaluation     = self.create_evaluation(p,k)
        return {
            "p": p,
            "k": k,
            "ds_training_id":   self.ds_training['DataSourceId'],
            "ds_evaluation_id": self.ds_evaluation['DataSourceId'],
            "model_id":         self.model['MLModelId'],
            "evaluation_id":    self.evaluation['EvaluationId'],
            # "evaluation_name":  self.evaluation['EvaluationName'],
            "rmse": None
         }

    def get_results(self):
        results = []
        for trial in self.trials:

            waiter = self.client.get_waiter('evaluation_available')
            print("Waiting on evaluation {0} to finish ".format( trial['evaluation_id'] ) )
            waiter.wait(FilterVariable='DataSourceId', EQ=trial['ds_evaluation_id'] )

            response = self.client.get_evaluation( EvaluationId=trial['evaluation_id'] )
            rmse     = float(response['PerformanceMetrics']['Properties']['RegressionRMSE'])
            trial["rmse"] = rmse
            results.append(trial)
            print("Evaluation score {0}".format(rmse))
        self.trials = results

    def delete_resources(self):
        # Now delete the resources
        print("Deleting datasources and model")
        for trial in self.trials:
            response = self.client.delete_data_source(
                DataSourceId = trial['ds_training_id']
            )
            response = self.client.delete_data_source(
                DataSourceId = trial['ds_evaluation_id']
            )
            response = self.client.delete_ml_model(
                MLModelId = trial['model_id']
            )

    def to_csv(self, filename):
        print("exporting to csv {0}".format(filename))
        keys = self.trials[0].keys()
        with open(filename, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.trials)

    def generate_sql(self, p):
        powers = [ 'power(x,{0}) as x{0}'.format(i) for i in range(1,p+1)  ]
        return 'select ' +  ','.join(powers) + ', y from nonlinear order by random()'

    def generate_data_rearrangement(self,split):
        if split == 'training':
            pct_begin = 0
            pct_end   = 70
        else:
            pct_begin = 70
            pct_end   = 100
        return json.dumps( { "splitting":{"percentBegin":pct_begin,"percentEnd":pct_end } } )

    def generate_schema(self, p):
        attributes = [ { "attributeName" : "x{0}".format(i), "attributeType" : "NUMERIC" } for i in range(1,p+1) ]
        attributes.append({ "attributeName" : "y", "attributeType" : "NUMERIC" })
        return json.dumps({ "version" : "1.0",
                "rowId" : None,
                "rowWeight" : None,
                "targetAttributeName" : "y",
                "dataFormat" : "CSV",\
                "dataFileContainsHeader" : False,
                "attributes" : attributes,
                "excludedAttributeNames" : [ ]
            })

    def create_datasource(self, p, k, split ):
        print("Create datasource {0} {1} {2} {3}".format(p,k,split, self.prefix))
        return self.client.create_data_source_from_redshift(
            DataSourceId    = "ds_{2}_{3}_p{0}_{1}".format(p,k,split, self.prefix),
            DataSourceName  = "DS {2} {3} p{0} {1}".format(p,k,split, self.prefix),
            DataSpec = {
                'DatabaseInformation': {
                    'DatabaseName': 'amlpacktdb',
                    'ClusterIdentifier': 'amlpackt'
                },
                'SelectSqlQuery': self.generate_sql(p),
                'DatabaseCredentials': {
                    'Username': 'alexperrier',
                    'Password': 'abcde'
                },
                'S3StagingLocation': 's3://aml.packt/data/ch9/',
                'DataRearrangement': self.generate_data_rearrangement(split),
                'DataSchema': self.generate_schema(p)
            },
            RoleARN='arn:aws:iam::17827751111:role/service-role/AmazonMLRedshift_us-east-1_amlpackt',
            ComputeStatistics=True
        )

    def create_model(self, p, k):
        print("Create model {0} {1} {2}".format(p, k, self.prefix))
        return self.client.create_ml_model(
            MLModelId   = "mdl_{2}_p{0}_{1}".format(p,k, self.prefix),
            MLModelName = "MDL {2} p{0} {1}".format(p,k, self.prefix),
            MLModelType = 'REGRESSION',
            Parameters  = self.sgd_parameters,
            TrainingDataSourceId = self.ds_training['DataSourceId'] ,
            Recipe   = json.dumps(self.recipe)
        )

    def create_evaluation(self, p, k):
        print("Create evaluation {0} {1} {2}".format(p, k, self.prefix))

        return self.client.create_evaluation(
                EvaluationId    = "eval_{2}_p{0}_{1}".format(p,k, self.prefix),
                EvaluationName  = "EVAL {2} p{0} {1}".format(p,k, self.prefix),
                MLModelId       = self.model['MLModelId'],
                EvaluationDataSourceId= self.ds_evaluation['DataSourceId']
            )

if __name__ == "__main__":
    max_p       = 2
    n_crossval  = 2
    prefix      = 'zorgl'
    nl = NonLinear(max_p, n_crossval, prefix)
    nl.run_all_trials()
    nl.get_results()
    nl.to_csv(filename)
    nl.delete_resources()


