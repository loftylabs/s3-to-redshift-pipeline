In this post I'm going to describe how to set up a simple mechanism for pipelining data from CSV files in an [S3](https://aws.amazon.com/documentation/s3/) bucket into corresponding [Redshift](https://aws.amazon.com/redshift/) database tables, using asynchronous [Celery](http://docs.celeryproject.org/en/latest/) tasks and Celery's [task scheduling](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html).

The basic idea here is that you have a database table in Redshift that you use for some other application (maybe you read data from the table into [Tableau](https://www.tableau.com/), for example), and you need to keep it continually updated from some other data source. Let's further suppose that data from this other source periodically shows up in a CSV file in an S3 bucket from which you can access it. (This scenario might sound familiar to certain retail analysts, for example.)

This toy app provides a simple example of a scalable pipeline mechanism for ingesting a single CSV schema into a matching database table. It is straightforward to scale this method up to many separate tables, updated from the matching CSVs. Furthermore, this approach can potentially handle both very large files, and a high degree of processing concurrency.

###Running the Application

####Prerequisites

Note that this post is about the data pipeline app itself, not setting up the AWS infrastructure (though we might cover some of that in a future post, so stay tuned). I'm going to assume that you have the following prerequisites:

- An Amazon Redshift database cluster, accessible via a [connection string](http://docs.aws.amazon.com/redshift/latest/mgmt/configuring-connections.html). Setting this up is a non-trivial task, but I'm going to assume that it's already been done.
- An Amazon S3 bucket. This part is rather easier to set up.
- Either an [IAM](http://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html) user configured with appropriate permissions, or AWS access keys, that can be used to allow the Redshift cluster to access the S3 bucket (as described [here](http://docs.aws.amazon.com/redshift/latest/dg/tutorial-loading-run-copy.html)).

####Downloading the Code

The code is available here: https://github.com/loftylabs/s3-to-redshift-pipeline. You'll need to update the project settings to the appropriate values, as described in the readme.

####Data File

For a simple example of a data schema, I used the training file from the [Kaggle Titanic Data Set](https://www.kaggle.com/c/titanic/data), and I'll refer you there for a description of the data. It's a pretty straightforward CSV. As we'll see shortly, I designed a simple database table matching this schema in which to load the data. In order to make the file work with the SQL `COPY` command that loads the data, I had to remove the first line in the CSV (the column names). I included the modifed file in the code repository.

A few notes about this:

- Other than the `CREATE TABLE` statement used the in the Flyway migration file (which we'll get to in a minute), nothing in this app is dependent on the structure of the data file. As long as you create a matching table, you could use most any CSV file without changing the rest of the app.
- It's a somewhat silly example data set, because the data never changes. But it's small and easy to carry around so it worked well in this context. Just remember that this same process will work just fine with much larger and more complex data sets.
- This file will be familiar to many people who have done some machine learning training, and I think it is a fairly fascinating--and sobering--dataset in its own right. Nevertheless, I'm just using it as a prop here. Most any other CSV file could be used, as long as the `CREATE TABLE` statement is updated accordingly.


####Upload the data file

You will need to get the data file into your S3 bucket one way or another. You can just use the AWS Console for that. Or, if you have the `AWS CLI` client set up, you can run (I used a bucket called `sa-data-pipeline-2`):
```bash
cd s3-to-redshift-pipeline/data_files
aws s3 cp . s3://sa-data-pipeline-2/pending/ --region=us-east-2 --recursive --exclude ".DS_Store"
```
This command is perhaps overkill here, but it's handy when you have a lot of files to upload at once.

####Create the Table with a Flyway Migration


Before loading the data, you'll need to set up your Redshift table. [Flyway](https://flywaydb.org/) is a handy way to do this (I just downloaded and extracted the Command Line tool bundle, without JRE, [here](https://flywaydb.org/getstarted/download), and threw away the stuff I didn't need).

In the `s3-to-redshift-pipeline/redshift/sql` folder, you'll find a file named `V1__initial_tables.sql` with the following contents:
```sql
CREATE TABLE titanic (
  PasengerId INT NOT NULL PRIMARY KEY distkey sortkey,
  Survived BOOLEAN NOT NULL,
  Pclass SMALLINT NOT NULL,
  Name VARCHAR(128) NOT NULL,
  Sex VARCHAR(8) NOT NULL,
  Age DECIMAL(3,1),
  SibSp SMALLINT NOT NULL,
  Parch SMALLINT NOT NULL,
  Ticket VARCHAR(32) NOT NULL,
  Fare DECIMAL(8,2),
  Cabin VARCHAR(16) NULL,
  Embarked CHAR(1)
);
```
First make sure that you set the `flyway.url` in the flyway conf file as explained in the repo readme, then run:
```bash
cd s3-to-redshift-pipeline/redshift
./flyway migrate
```

*Note:* You don't *have* to use Flyway for this, it's just a handy way to manage database migrations so I included it here. If you have another convenient way you prefer to run SQL against your Redshift database that will work fine too, just run the `CREATE TABLE` statement above.

####Running the Celery App

Before you can run the app you'll need to update the settings as described in the readme:

- Replace `[redshift host URL]` in `redshift/conf/flyway.conf` with the URL for your Redshift cluster
- Replace the following in `pipeline/settings.py` with the appropriate values:
    - `[aws access key]`
    - `[aws secret key]`
    - `[redshift host URL]`
    - `[db name]`
    - `[db username]`
    - `[db password]`
    - `[S3 bucket name]`
    
You'll also need to have Python 2.7 and [Virtualenv](https://virtualenv.pypa.io/en/stable/) installed in your development environment.

Once you have all that set up, you can get the app up and running with:

```bash
cd s3-to-redshift-pipeline
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

*Note:* I installed [`ipython`](http://ipython.org/) because I like using it, but it's definitely not required for this app, and comes with lots of dependencies. If you want to keep your virtualenv clean, this is all you really need:
```bash
pip install celery
pip install sqlalchemy
pip install boto3
pip install psycopg2
```

Once your virtual environment is set up and ready to go, you can run the app with:
```bash
celery worker -A pipeline.celeryapp -B
```

*Note:* For local development and testing purposes, I usually find this command a bit more helpful:
```bash
celery worker -A pipeline.celeryapp -B --concurrency=1 --loglevel=info --purge
```


###The Code

In this post we walked through setting up the app and getting it to work. In a future blog post I will go through the code in some detail, and explain some ways it could pretty easily be extended. In the meantime, though, the code is available on [Github]( https://github.com/loftylabs/s3-to-redshift-pipeline), so feel free to download play with it. Do let us know if you have any questions!