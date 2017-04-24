#!/bin/bash

for k in 1 2 3 4 5 
do
    filename="data/shuffled_$k.csv"
    gshuf data/ames_housing_nohead.csv -o data/ames_housing_nohead.csv
    cat data/ames_housing_header.csv data/ames_housing_nohead.csv > tmp.csv; mv tmp.csv $filename
    aws s3 cp ./$filename s3://aml.packt/data/ch8/
done
