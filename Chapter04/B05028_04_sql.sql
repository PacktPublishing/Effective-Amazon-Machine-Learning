# -----------------------------------------------------------------------------
#  SQL and query results for chapter 8
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#  A brief tour of AWS Athena
# -----------------------------------------------------------------------------

CREATE EXTERNAL TABLE temp ();


# -----------------------------------------------------------------------------
#  Creating the database and table directly in SQL
# -----------------------------------------------------------------------------


CREATE DATABASE titanic_db;

# -----------------------------------------------------------------------------
CREATE EXTERNAL TABLE IF NOT EXISTS titanic_db.titanic (
        pclass tinyint,
        survived tinyint,
        name string,
        sex string,
        age double,
        sibsp tinyint,
        parch tinyint,
        ticket string,
        fare double,
        cabin string,
        embarked string,
        boat string,
        body string,
        home_dest string
    )
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
    WITH SERDEPROPERTIES (
        'serialization.format' = ',',
        'field.delim' = ','
    ) LOCATION 's3://aml.packt/athena_data/'

# -----------------------------------------------------------------------------
#  Missing values
# -----------------------------------------------------------------------------

select coalesce(age, 28) as age, coalesce(fare, 14.5) as fare from titanic;

# -----------------------------------------------------------------------------
SELECT age, CASE
    WHEN age is null THEN 0
    ELSE 1
    END as is_age_missing
from titanic;


# -----------------------------------------------------------------------------
#  Handling outliers in the fare
# -----------------------------------------------------------------------------

select fare, log(fare +1, 2) as log_fare from titanic;

# -----------------------------------------------------------------------------
--   Extracting the title from the name
# -----------------------------------------------------------------------------
SELECT name, split(name, ' ')[2] as title from titanic;

# -----------------------------------------------------------------------------
#   Inferring the deck from the cabin
# -----------------------------------------------------------------------------

SELECT cabin, substr(cabin, 1, 1) as deck  FROM titanic;

# -----------------------------------------------------------------------------
#   Calculating family size
# -----------------------------------------------------------------------------

select sibps + parch + 1 as family_size from titanic;

# -----------------------------------------------------------------------------
#  Wrapping up
# -----------------------------------------------------------------------------


SELECT pclass,
survived,
name,
sex,
COALESCE(age, 28) as age,
sibsp,
parch,
ticket,
COALESCE(fare, 14.5) as fare,
cabin,
embarked,
boat,
body,
home_dest,
CASE
 WHEN age is null THEN 0
 ELSE 1
 END as is_age_missing,
log(fare + 1, 2) as log_fare,
split(name, ' ')[2] as title,
substr(cabin, 1, 1) as deck,
sibsp + parch + 1 as family_size
FROM titanic
ORDER BY RAND();





