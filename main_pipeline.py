### โค้ดนี้ ใช้ Google Data Flow ซึ่งเป็น Cloud Service ทำ Cleansing on the fly ที่สามารถปรับแต่งข้อมูลแต่ละ event อย่างต่อเนื่องและ write ลง database (BigQuery) ในทันที

import apache_beam as beam
import logging
from your_project_name.cleanse_data_module import cleanse_data  # Change to your project name and module

logging.basicConfig(level=logging.INFO)

# Specify your BigQuery project ID and dataset.table name
table_spec = (
    'powerful-axon-437502-r4:'
    'workshop-dataops-bucket.aekanun_dfsqltable_sales'
)

# Define the schema for your BigQuery table
schema = (
    'tr_time_str:DATETIME, first_name:STRING, last_name:STRING, '
    'city:STRING, state:STRING, product:STRING, amount:FLOAT, '
    'dayofweek:INTEGER'
)

# List of pipeline arguments; Adjust with your Google Cloud settings
pipeline_args = [
    '--project=powerful-axon-437502-r4',  # Change to your GCP project ID
    '--runner=DataflowRunner',
    '--region=us-central1',  # Adjust as per your GCP region
    '--staging_location=gs://workshop-dataops-bucket/temp/staging/',  # Change to your bucket path
    '--temp_location=gs://workshop-dataops-bucket/temp',  # Change to your bucket path
    '--streaming',
    '--setup_file=./setup.py',  # Point to your setup file
]

pipeline_options = beam.options.pipeline_options.PipelineOptions(pipeline_args)
p = beam.Pipeline(options=pipeline_options)

(p 
 | 'Read from PubSub' >> beam.io.ReadFromPubSub(
     topic="projects/powerful-axon-437502-r4/topics/aekanun-transactions"  # Change to your PubSub topic
 )
 | 'Cleanse Data' >> beam.Map(cleanse_data)  # Referencing the cleansing function
 | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
       table=table_spec,
       schema=schema,
       write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
       create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
   )
)

result = p.run()
result.wait_until_finish()

# Grabbing job ID and region info to save in a file
job_id = result._job.id
region = 'us-central1'  # Adjust as per your GCP region

with open("job_info.txt", "w") as file:
    file.write(f"{job_id}\n{region}")
