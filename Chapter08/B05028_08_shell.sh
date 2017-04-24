# -----------------------------------------------------------------------------
#  Shell command line for chapter 8
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#  Connecting through the command line
# -----------------------------------------------------------------------------

$ psql --host=amlpackt.cenllwot8v9r.us-east-1.redshift.amazonaws.com \
--port=5439 --username=alexperrier --password --dbname=amlpacktdb

# -----------------------------------------------------------------------------
# Load file on S3
$ aws s3 cp data/titanic.csv s3://aml.packt/data/ch9/
# connect to database via psql
$ psql --host=amlpackt.cenllwot8v9r.us-east-1.redshift.amazonaws.com \
--port=5439 --username=alexperrier --password --dbname=amlpacktdb
# upload data from your S3 location into the titanic table
$ copy titanic from 's3://aml.packt/data/ch9/titanic.csv'
CREDENTIALS 'aws_access_key_id=<access key id>;aws_secret_access_key=<access secret key>'
CSV;


# -----------------------------------------------------------------------------
#  Executing Redshift queries using Psql
# -----------------------------------------------------------------------------

$ psql -h amlpackt.cenllwot8v9r.us-east-1.redshift.amazonaws.com \
-p 5439 -U alexperrier --password -d amlpacktdb


# -----------------------------------------------------------------------------
$ export REDSHIFT_CONNECT='-h amlpackt.cenllwot8v9r.us-east-1.redshift.amazonaws.com -p 5439 -U alexperrier -d amlpacktdb'

# -----------------------------------------------------------------------------
$ export PGPASSWORD=your_password

# -----------------------------------------------------------------------------
$ psql $REDSHIFT_CONNECT

# -----------------------------------------------------------------------------
psql $REDSHIFT_CONNECT
alexperrier@amlpacktdb=> select count(*) from titanic;

# -----------------------------------------------------------------------------
$ psql $REDSHIFT_CONNECT -f my_file.sql

# -----------------------------------------------------------------------------

$ psql $REDSHIFT_CONNECT -c 'SELECT count(*) FROM my_table'

# -----------------------------------------------------------------------------
#  Uploading the nonlinear data to Redshift
# -----------------------------------------------------------------------------
$ psql $REDSHIFT_CONNECT -c "select count(*) from nonlinear"
> count
> 1000
>(1 row)









