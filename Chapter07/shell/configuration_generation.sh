#!/bin/bash

for k in 1 2 3 4 5 
do
    # training datasource
    sed 's/{k}/1/g' data/templates/dsrc_training_template.json > data/cfg/dsrc_training_00$k.json

    # evaluation datasource
    sed 's/{k}/1/g' data/templates/dsrc_validate_template.json > data/cfg/dsrc_validate_00$k.json

    # L2 model
    sed 's/{k}/1/g' data/templates/mdl_l2_template.json > data/cfg/mdl_l2_00$k.json

    # L2 evaluation
    sed 's/{k}/1/g' data/templates/eval_l2_template.json > data/cfg/eval_l2_00$k.json

    # L1 model
    sed 's/{k}/1/g' data/templates/mdl_l1_template.json > data/cfg/mdl_l1_00$k.json

    # L1 evaluation
    sed 's/{k}/1/g' data/templates/eval_l1_template.json > data/cfg/eval_l1_00$k.json

done
