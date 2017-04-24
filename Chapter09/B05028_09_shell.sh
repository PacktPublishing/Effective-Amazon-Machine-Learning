# -----------------------------------------------------------------------------
#  Shell command line for chapter 9
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#  Producing tweets
# -----------------------------------------------------------------------------

$ watch -n 600 python producer.py

# -----------------------------------------------------------------------------
# The Redshift database
# -----------------------------------------------------------------------------
$ psql --host=vegetables.cenllwot8v9r.us-east-1.redshift.amazonaws.com \
    --port=5439 --username=alexperrier --password --dbname=vegetablesdb

# -----------------------------------------------------------------------------
#  Download the dataset from RedShift
# -----------------------------------------------------------------------------

# Download
$ aws s3 cp s3://aml.packt/data/veggies/results/0000_part_00 data/
$ aws s3 cp s3://aml.packt/data/veggies/results/0001_part_00 data/
# Combine
$ cp data/0000_part_00 data/veggie_tweets.tmp
$ cat data/0001_part_00 >> data/veggie_tweets.tmp
# -----------------------------------------------------------------------------

$ sed 's/|/,/g' data/veggie_tweets.tmp > data/veggie_tweets.csv