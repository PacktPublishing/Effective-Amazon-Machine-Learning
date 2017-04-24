# -----------------------------------------------------------------------------
#  SQL and query results for chapter 9
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#  The Redshift database
# -----------------------------------------------------------------------------


CREATE TABLE IF NOT EXISTS tweets (
    id BIGINT primary key,
    screen_name varchar(255),
    veggie varchar(255),
    text varchar(65535)
);


# -----------------------------------------------------------------------------
#  Adding Redshift to the Kinesis Firehose
# -----------------------------------------------------------------------------

COPY tweets (id,screen_name, veggie,tb_polarity, text)
FROM 's3://aml.packt/<manifest>'
CREDENTIALS 'aws_iam_role=arn:aws:iam::<aws-account-id>:role/<role-name>'
MANIFEST delimiter ',';



# -----------------------------------------------------------------------------
#  Preprocessing with Lambda
# -----------------------------------------------------------------------------
drop table if exists tweets;
CREATE TABLE IF NOT EXISTS tweets (
    id BIGINT primary key,
    screen_name varchar(255),
    veggie varchar(255),
    ml_label int,
    ml_score float,
    text varchar(65535)
);


# -----------------------------------------------------------------------------
#  Download the dataset from RedShift
# -----------------------------------------------------------------------------

unload ('select * from tweets') to 's3://aml.packt/data/veggies/results/'
iam_role 'arn:aws:iam::0123456789012:role/MyRedshiftRole';



