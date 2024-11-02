import apache_beam as beam
import logging
import json
from apache_beam.options.pipeline_options import StandardOptions, PipelineOptions

logging.getLogger().setLevel(logging.INFO)

# Specify your BigQuery project ID and dataset.table name
table_spec = 'stately-gist-435602-u9:aekanun_workshop2.aekanun_dfsqltable_sales'

# Define the schema for your BigQuery table
schema = (
    'tr_time_str:DATETIME, first_name:STRING, last_name:STRING, '
    'city:STRING, state:STRING, product:STRING, amount:FLOAT, '
    'dayofweek:INTEGER'
)

# Parse and validate PubSub messages
def parse_pubsub(element):
    try:
        return json.loads(element.decode('utf-8'))
    except Exception as e:
        logging.error(f"Error parsing message: {e}")
        return None

# Define pipeline options
pipeline_options = PipelineOptions([
    f'--project=stately-gist-435602-u9',
    '--runner=DataflowRunner',
    '--region=us-central1',
    f'--staging_location=gs://aekanun_workshop2/temp/staging/',
    f'--temp_location=gs://aekanun_workshop2/temp',
    '--setup_file=./setup.py',
    '--max_num_workers=5',
    '--enable_streaming_engine',
    '--enable_windowed_writes',
    '--experiments=use_beam_bq_sink'
])

# Set streaming mode
pipeline_options.view_as(StandardOptions).streaming = True

# Create pipeline
p = beam.Pipeline(options=pipeline_options)

# Define subscription path (แนะนำให้ใช้ subscription แทน topic)
subscription = 'projects/stately-gist-435602-u9/subscriptions/aekanun-transactions-sub'

# Build pipeline
(p 
 | 'Read from PubSub' >> beam.io.ReadFromPubSub(
     subscription=subscription
 )
 | 'Parse JSON' >> beam.Map(parse_pubsub)
 | 'Filter None' >> beam.Filter(lambda x: x is not None)
 | 'Cleanse Data' >> beam.Map(cleanse_data)
 | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
     table=table_spec,
     schema=schema,
     write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
     create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
     batch_size=100,  # Adjust based on your needs
     triggering_frequency=60,  # Flush every 60 seconds
     method='STREAMING_INSERTS'
   )
)

# Run pipeline
result = p.run()
logging.info("Pipeline started...")

try:
    # Save job info
    job_id = result._job.id
    region = 'us-central1'
    with open("job_info.txt", "w") as file:
        file.write(f"{job_id}\n{region}")
    logging.info(f"Job ID: {job_id} saved to job_info.txt")
    
    # Wait for pipeline to finish
    result.wait_until_finish()
except KeyboardInterrupt:
    logging.info("Pipeline interrupted by user")
    result.cancel()
except Exception as e:
    logging.error(f"Pipeline error: {e}")
    raise