
# -----------------------------------------------------------------------------
#  The following commands are used to parse the Amazon ML logs
#  The original file is test.txt
#  see for instance log/titanic_training.log
#  sample original line is:
#  16/12/24 12:45:52 INFO: learner-id=1050 model-convergence:         negative-log-likelihood=1.000000e+00 (delta=1.000000e+00) is-converged=no

# -----------------------------------------------------------------------------

# replace ' INFO: learner-id=' by ,,
sed 's/ INFO: learner-id=/,,/g' test.txt > test2.txt
cp test2.txt test.txt

# replace ' model-performance:         accuracy=' by ,
sed 's/ model-performance:         accuracy=/,/g' test.txt > test2.txt
cp test2.txt test.txt

# replace ' recall=' by ,
sed 's/ recall=/,/g' test.txt > test2.txt
cp test2.txt test.txt

# replace ' precision=' by ,
sed 's/ precision=/,/g' test.txt > test2.txt
cp test2.txt test.txt

# replace ' f1-score=' by ,
sed 's/ f1-score=/,/g' test.txt > test2.txt
cp test2.txt test.txt

# replace ' auc=' by ,
sed 's/ auc=/,/g' test.txt > test2.txt
cp test2.txt test.txt



# replace ' INFO: learner-id=' by ,
sed 's/ INFO: learner-id=/,,/g' test.txt > test2.txt
cp test2.txt test.txt

# replace ' model-convergence:         negative-log-likelihood=' by ,
sed 's/ model-convergence:         negative-log-likelihood=/,/g' test.txt > test2.txt
cp test2.txt test.txt

# replace ' (delta=1.000000e+00) is-converged=no' by ,
sed 's/ (delta=1.000000e+00) is-converged=no//g' test.txt > test2.txt
cp test2.txt test.txt
