# -----------------------------------------------------------------------------
#  Shell command line for chapter 5
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#  Parsing the model logs
# -----------------------------------------------------------------------------
grep "model-performance:" model.log >> model_performance.tmp

# -----------------------------------------------------------------------------
sed -i.bak 's/STRING_TO_REPLACE/STRING_TO_REPLACE_IT/g' filename

# -----------------------------------------------------------------------------
sed -i.bak 's/ INFO: learner-id=/,/g' model_performance.tmp

# -----------------------------------------------------------------------------
sed -i.bak 's/ INFO: learner-id=/,,/g' model_performance.tmp
sed -i.bak 's/ model-performance:         accuracy=/,/g' model_performance.tmp
sed -i.bak 's/ recall=/,/g' model_performance.tmp
sed -i.bak 's/ precision=/,/g' model_performance.tmp
sed -i.bak 's/ f1-score=/,/g' model_performance.tmp
sed -i.bak 's/ auc=/,/g' model_performance.tmp

# -----------------------------------------------------------------------------
sed -i.bak 's/ INFO: learner-id=/,,/g' filename
sed -i.bak 's/ model-convergence:         negative-log-likelihood=/,/g' filename
sed -i.bak 's/ (delta=1.000000e+00) is-converged=no//g' filename
