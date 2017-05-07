BROKER_URL = 'amqp://guest@localhost:5672/'

DATABASE_CONNECTION_STRING = 'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'.format(
    db_host='[redshift host URL]',
    db_port=5439,
    db_name='[db name]',
    db_user='[db username]',
    db_password='[db password]'
)

INPUT_BUCKET_NAME = '[S3 bucket name]'

AWS_ACCESS_KEY = '[aws access key]'
AWS_SECRET_KEY = '[aws secret key]'

# run task every 30 minutes
BEAT_INTERVAL = 30 * 60
