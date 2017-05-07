import logging

import boto3
from botocore.client import Config
import datetime

from pipeline.settings import AWS_ACCESS_KEY, AWS_SECRET_KEY


logger = logging.getLogger(__name__)

CLIENT = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY,
                      config=Config(signature_version='s3v4', region_name='us-east-2'))


class S3Tools(object):

    @staticmethod
    def move_file_processed(bucket, old_path):
        today = datetime.date.today()
        new_path = old_path.replace('pending', 'processed/%s/%s/%s' % (today.year, today.month, today.day))

        CLIENT.copy({"Bucket": bucket, "Key": old_path}, bucket, new_path)
        CLIENT.delete_object(Bucket=bucket, Key=old_path)

        logger.info('Moved "{0}" to "{1}'.format(old_path, new_path))

        return bucket, new_path

    @staticmethod
    def get_signed_s3_url(bucket, key):
        if bucket and key:
            return CLIENT.generate_presigned_url('get_object',
                                                 Params={'Bucket': bucket, 'Key': key},
                                                 ExpiresIn=300)

    @staticmethod
    def get_file_contents(bucket, key):
        if bucket and key:
            s3 = boto3.resource('s3', config=Config(signature_version='s3v4', region_name='us-east-2'))
            return s3.Object(bucket, key).get()['Body']

    @staticmethod
    def list_folder_contents(bucket, prefix):
        return CLIENT.list_objects_v2(Bucket=bucket, Prefix=prefix, StartAfter=prefix)

    @staticmethod
    def list_files_in_folder(bucket, prefix):
        contents = S3Tools.list_folder_contents(bucket, prefix)['Contents']
        return [x['Key'] for x in contents if x['Size'] > 0]
