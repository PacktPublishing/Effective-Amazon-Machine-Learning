# -----------------------------------------------------------------------------
#  SQL and query results for chapter 8
# -----------------------------------------------------------------------------


alexperrier@amlpacktdb=> dt
 No relations found.

# -----------------------------------------------------------------------------

alexperrier@amlpacktdb=> copy <table name> from '<s3 path to csv file>' \
CREDENTIALS 'aws_access_key_id=<aws access key id>;aws_secret_access_key=<aws secret access key>'
CSV;

# -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS titanic (
    id integer primary key,
    pclass integer,
    survived boolean,
    name varchar(255),
    sex varchar(255),
    age real,
    sibsp integer,
    parch integer,
    ticket varchar(255),
    fare real,
    cabin varchar(255),
    embarked char(1),
    boat varchar(8),
    body varchar(8),
    home_dest varchar(255)
);

# -----------------------------------------------------------------------------
alexperrier@amlpacktdb=> dt
 List of relations
 Schema | Name | Type | Owner
 --------+---------+-------+-------------
 public | titanic | table | alexperrier
 (1 row)

# -----------------------------------------------------------------------------
alexperrier@amlpacktdb=> d+ titanic
 Table "public.titanic"
 Column | Type | Modifiers | Storage | Stats target | Description
 -----------+------------------------+------------------------------------------------------+----------+--------------+-------------
 id | integer | not null default nextval('titanic_id_seq'::regclass) | plain | |
 pclass | integer | | plain | |
 survived | boolean | | plain | |
 name | character varying(255) | | extended | |
 sex | character varying(255) | | extended | |
 age | real | | plain | |
 sibsp | integer | | plain | |
 parch | integer | | plain | |
 ticket | character varying(255) | | extended | |
 fare | real | | plain | |
 cabin | character varying(255) | | extended | |
 embarked | character(1) | | extended | |
 boat | character varying(8) | | extended | |
 body | character varying(8) | | extended | |
 home_dest | character varying(255) | | extended | |
 Indexes:
 "titanic_pkey" PRIMARY KEY, btree (id)

# -----------------------------------------------------------------------------
alexperrier@amlpacktdb=> select count(*) from titanic;
 -[ RECORD 1 ]
 count | 1309

# -----------------------------------------------------------------------------
#  Uploading the nonlinear data to Redshift
# -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS nonlinear (
  id integer primary key,
  x1 real,
  y real
);

# -----------------------------------------------------------------------------
copy nonlinear from 's3://aml.packt/data/ch9/nonlinear.csv'
CREDENTIALS 'aws_access_key_id=<access key id>;aws_secret_access_key=<access secret key>'
CSV;

# -----------------------------------------------------------------------------
#  Polynomial regression in Amazon ML
# -----------------------------------------------------------------------------


select x, power(x,2) as x2, y from nonlinear order by random()

# -----------------------------------------------------------------------------
select x, power(x,2) as x2, power(x,3) as x3, y from nonlinear order by random()











