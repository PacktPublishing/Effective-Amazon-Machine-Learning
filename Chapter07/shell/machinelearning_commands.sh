#!/bin/bash

# for k in 1 2 3 4 5 
for k in 1 2
do
    # create datasources for training
    aws machinelearning create-data-source-from-s3 --cli-input-json file://data/cfg/dsrc_kfold_training_00$k.json

    # create datasources for evaluation
    aws machinelearning create-data-source-from-s3 --cli-input-json file://data/cfg/dsrc_kfold_validate_00$k.json

    # train models with L2 regularization 
    aws machinelearning create-ml-model --cli-input-json file://data/cfg/mdl_l2_00$k.json

    # train models with L1 regularization 
    aws machinelearning create-ml-model --cli-input-json file://data/cfg/mdl_l1_00$k.json

    # apply L2 models to evaluation datasources
    aws machinelearning create-evaluation --cli-input-json file://cfg/eval_l2_00$k.json

    # apply L1 models to evaluation datasources
    aws machinelearning create-evaluation --cli-input-json file://cfg/eval_l1_00$k.json
done


# Get evaluation results for L2 regularization
aws machinelearning get-evaluation --evaluation-id CH8_AH_L2_00$k | grep RegressionRMSE > l2_model.log

# Get evaluation results for L1 regularization
aws machinelearning get-evaluation --evaluation-id CH8_AH_L1_00$k | grep RegressionRMSE > l1_model.log
