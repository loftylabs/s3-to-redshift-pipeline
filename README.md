# s3-to-redshift-pipeline
toy celery data-pipeline app for blog post


## Setup

#### Clone repo:
```bash
git clone https://github.com/loftylabs/s3-to-redshift-pipeline.git
```

#### Install requirements:
```bash
cd s3-to-redshift-pipeline
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Create Redshift table:
Replace `[redshift host URL]` in `redshift/conf/flyway.conf` with the URL for your Redshift cluster, then run:
```bash
cd s3-to-redshift-pipeline/redshift
./flyway migrate
```


#### Python Settings

Replace the following in `pipeline/settings.py` with the appropriate values:
- `[aws access key]`
- `[aws secret key]`
- `[redshift host URL]`
- `[db name]`
- `[db username]`
- `[db password]`
- `[S3 bucket name]`

If desired, you can change the celery beat scheduling interval from 30 minutes to something else by changing `BEAT_INTERVAL` in `pipeline/settings.py`.


#### Run celery worker
```bash
# with the virtualenv activated:
celery worker -A pipeline.celeryapp -B
```
