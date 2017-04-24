# -----------------------------------------------------------------------------
#  Shell command line for chapter 7
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#  Installing AWS CLI
# -----------------------------------------------------------------------------
$ pip install --upgrade --user awscli

$ export PATH=~/.local/bin:$PATH
$ source ~/.bash_profile
$ aws --version
aws-cli/1.11.47 Python/3.5.2 Darwin/15.6.0 botocore/1.5.10
$ aws configure

$ aws configure

AWS Access Key ID [None]: ABCDEF_THISISANEXAMPLE
AWS Secret Access Key [None]: abcdefghijk_THISISANEXAMPLE
Default region name [None]: us-west-2
Default output format [None]: json

$ aws configure --profile user2

~/.aws/config

[default]
output = json
region = us-east-1

[profile user2]
output = text
region = us-west-2

~/.aws/credentials

[default]
aws_secret_access_key = ABCDEF_THISISANEXAMPLE
aws_access_key_id = abcdefghijk_THISISANEXAMPLE

[user2]
aws_access_key_id = ABCDEF_ANOTHERKEY
aws_secret_access_key = abcdefghijk_ANOTHERKEY

# -----------------------------------------------------------------------------
#  Picking up CLI syntax
# -----------------------------------------------------------------------------


$ aws <service> [options] <command> <subcommand> [parameters]

$ aws s3 ls aml.packt

$ aws <service> help

$ aws s3 <command> sourceURI destinationURI  [parameters]

$ aws s3 cp /tmp/foo/ s3://The_Bucket/ --recursive --exclude "*" --include "*.jpg"

# -----------------------------------------------------------------------------
#  Passing parameters using JSON files
# -----------------------------------------------------------------------------

$ aws machinelearning create-ml-model --generate-cli-skeleton

$ aws machinelearning create-ml-model --generate-cli-skeleton > filename.json

$ aws machinelearning create-ml-model file://filename.json

# -----------------------------------------------------------------------------
#  Splitting the dataset with shell commands
# -----------------------------------------------------------------------------

$ head -n 1 ames_housing.csv > ames_housing_header.csv

$ tail -n +2 ames_housing.csv > ames_housing_nohead.csv

$ gshuf ames_housing_nohead.csv -o ames_housing_nohead.csv

$ head -n 2050 ames_housing_nohead.csv > ames_housing_training.csv

$ tail -n 880 ames_housing_nohead.csv > ames_housing_validate.csv

$ cat ames_housing_header.csv ames_housing_training.csv > tmp.csv
$ mv tmp.csv ames_housing_training.csv

$ cat ames_housing_header.csv ames_housing_validate.csv > tmp.csv
$ mv tmp.csv ames_housing_validate.csv

# -----------------------------------------------------------------------------
#  A simple project using the CLI
# -----------------------------------------------------------------------------

$ aws s3 cp ./ames_housing_training.csv s3://aml.packt/data/ch8/
upload: ./ames_housing_training.csv to s3://aml.packt/data/ch8/ames_housing_training.csv

$ aws s3 cp ./ames_housing_validate.csv s3://aml.packt/data/ch8/
upload: ./ames_housing_validate.csv to s3://aml.packt/data/ch8/ames_housing_validate.csv

# -----------------------------------------------------------------------------
#  Creating the datasource
# -----------------------------------------------------------------------------

$ aws machinelearning create-data-source-from-s3 --generate-cli-skeleton


$ gshuf ames_housing_nohead.csv -o ames_housing_nohead.csv
$ cat ames_housing_header.csv ames_housing_nohead.csv > tmp.csv
$ mv tmp.csv ames_housing_shuffled.csv
$ aws s3 cp ./ames_housing_shuffled.csv s3://aml.packt/data/ch8/

$ aws machinelearning create-data-source-from-s3 --cli-input-json file://dsrc_ames_housing_001.json


$ aws machinelearning  get-data-source --data-source-id ch8_ames_housing_001

# -----------------------------------------------------------------------------
#  Creating the model
# -----------------------------------------------------------------------------

$ aws machinelearning create-ml-model --generate-cli-skeleton > mdl_ames_housing_001.json

$ aws machinelearning create-ml-model --cli-input-json file://mdl_ames_housing_001.json

$ aws machinelearning get-ml-model --ml-model-id ch8_ames_housing_001

$ watch -n 10 aws machinelearning get-ml-model --ml-model-id ch8_ames_housing_001

# -----------------------------------------------------------------------------
#  Evaluating our model with create-evaluation
# -----------------------------------------------------------------------------

$ aws machinelearning create-evaluation --generate-cli-skeleton > eval_ames_housing_001.json

$ aws machinelearning create-evaluation --cli-input-json file://eval_ames_housing_001.json

$ aws machinelearning get-evaluation --evaluation-id ch8_ames_housing_001

# -----------------------------------------------------------------------------
#  Generating the shuffled datasets
# -----------------------------------------------------------------------------

#!/bin/bash
for k in 1 2 3 4 5
do
    filename="data/ames_housing_shuffled_$k.csv"
    gshuf data/ames_housing_nohead.csv -o data/ames_housing_nohead.csv
    cat data/ames_housing_header.csv data/ames_housing_nohead.csv > tmp.csv;
    mv tmp.csv $filename
    aws s3 cp ./$filename s3://aml.packt/data/ch8/
done


# -----------------------------------------------------------------------------
#  Generating the evaluations template
# -----------------------------------------------------------------------------

#!/bin/bash
for k in 1 2 3 4 5
do
    # training datasource
    sed 's/{k}/1/g' data/templates/dsrc_training_template.json > data/cfg
    /dsrc_training_00$k.json

    # evaluation datasource
    sed 's/{k}/1/g' data/templates/dsrc_validate_template.json > data/cfg
    /dsrc_validate_00$k.json

    # L2 model
    sed 's/{k}/1/g' data/templates/mdl_l2_template.json > data/cfg
    /mdl_l2_00$k.json

    # L2 evaluation
    sed 's/{k}/1/g' data/templates/eval_l2_template.json > data/cfg
    /eval_l2_00$k.json

    # L1 model
    sed 's/{k}/1/g' data/templates/mdl_l1_template.json > data/cfg
    /mdl_l1_00$k.json

    # L1 evaluation
    sed 's/{k}/1/g' data/templates/eval_l1_template.json > data/cfg
    /eval_l1_00$k.json

done

# -------------

#!/bin/bash
for k in 1 2 3 4 5
do
    aws machinelearning create-data-source-from-s3 --cli-input-json
    file://data/cfg/dsrc_kfold_training_00$k.json
    aws machinelearning create-data-source-from-s3 --cli-input-json
    file://data/cfg/dsrc_kfold_validate_00$k.json
done


# -------------
#!/bin/bash
for k in 1 2 3 4 5
    aws machinelearning create-ml-model --cli-input-json file://data
    /cfg/mdl_l2_00$k.json
    aws machinelearning create-ml-model --cli-input-json file://data
    /cfg/mdl_l1_00$k.json
done

# -------------
#!/bin/bash
for k in 1 2 3 4 5
    aws machinelearning create-evaluation --cli-input-json file://cfg
    /eval_l2_00$k.json
    aws machinelearning create-evaluation --cli-input-json file://cfg
    /eval_l1_00$k.json
done

# -------------
#!/bin/bash
for k in 1 2 3 4 5
    aws machinelearning get-evaluation --evaluation-id CH8_AH_L2_00$k |
    grep RegressionRMSE >> l2_model_rmse.log
    aws machinelearning get-evaluation --evaluation-id CH8_AH_L1_00$k |
    grep RegressionRMSE >> l1_model_rmse.log
done



