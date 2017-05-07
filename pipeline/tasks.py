import re
import logging

from datetime import datetime
from sqlalchemy import create_engine

import pipeline.settings as settings
from pipeline.s3_tools import S3Tools
from pipeline.celeryapp import app


logger = logging.getLogger(__name__)


sql_engine = create_engine(settings.DATABASE_CONNECTION_STRING)


@app.task
def load_data():
    logger.info('scanning for files...')
    for file_key in S3Tools.list_files_in_folder(bucket=settings.INPUT_BUCKET_NAME, prefix='pending'):
        load_data_file.delay(file_key)


@app.task
def load_data_file(file_key):

    logger.warn('file_key: {0}'.format(file_key))

    pattern = r'pending/(?P<file_name>[\w -.]+)'
    re_match = re.match(pattern, file_key)

    if re_match:
        file_name = re_match.group('file_name')

        sql = upsert_scripts_by_filename[file_name]

        logger.info('file_name: {0}'.format(file_name))
        logger.info('sql: {0}'.format(sql))
        logger.info('executing...')

        start_time = datetime.now()
        sql_engine.execute(sql)

        S3Tools.move_file_processed(bucket=settings.INPUT_BUCKET_NAME,
                                    old_path=file_key)

        logger.info('done. elapsed: {0}'.format(datetime.now() - start_time))

    else:
        raise Exception('unable to parse file key')


upsert_scripts_by_filename = {
    'kaggle-titanic-training-data.csv':
'''
CREATE TABLE titanic_staging(like titanic INCLUDING DEFAULTS);

COPY titanic_staging
FROM 's3://sa-data-pipeline-2/pending/kaggle-titanic-training-data.csv'
WITH CREDENTIALS 'aws_iam_role=arn:aws:iam::257550492394:role/hiRedshiftS3'
DELIMITER ','
csv;

DELETE from titanic
USING titanic_staging
WHERE titanic.PasengerId = titanic_staging.PasengerId;

INSERT INTO titanic SELECT * FROM titanic_staging;

DROP TABLE titanic_staging;
'''
}
