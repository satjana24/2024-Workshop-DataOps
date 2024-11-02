provider "google" {
  credentials = file("stately-gist-435602-u9-e7d9d76c1b6d.json")
  project     = "stately-gist-435602-u9"
  region      = "us-central1"  # กำหนด default region
}

# Cloud Storage bucket สำหรับเก็บข้อมูล
resource "google_storage_bucket" "bucket" {
  name          = "aekanun_workshop2"
  location      = "us-south1"
  force_destroy = true
  
  # การตั้งค่าเพิ่มเติมสำหรับความปลอดภัย
  uniform_bucket_level_access = true
  versioning {
    enabled = false
  }
}

# BigQuery Dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = "aekanun_workshop2"
  friendly_name              = "Workshop 2 Dataset"
  description                = "Dataset for workshop 2"
  location                   = "US"
  delete_contents_on_destroy = true

  # การตั้งค่าการหมดอายุของข้อมูล (ถ้าต้องการ)
  default_table_expiration_ms = null  # ไม่มีการหมดอายุ

  # การตั้งค่าการเข้าถึง
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }
  access {
    role          = "READER"
    special_group = "projectReaders"
  }
  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }
}

# สร้าง Dataflow job
resource "null_resource" "main_pipeline" {
  provisioner "local-exec" {
    command = <<-EOT
      export GOOGLE_APPLICATION_CREDENTIALS="${path.module}/stately-gist-435602-u9-e7d9d76c1b6d.json"
      python3 main_pipeline.py
    EOT
  }
  depends_on = [
    google_bigquery_dataset.dataset,
    google_storage_bucket.bucket
  ]
}

# Resource สำหรับหยุด Dataflow job เมื่อ destroy
resource "null_resource" "stop_dataflow_job_on_destroy" {
  provisioner "local-exec" {
    when    = destroy
    command = "gcloud dataflow jobs cancel $(head -n 1 job_info.txt) --region=$(tail -n 1 job_info.txt)"
  }
  depends_on = [null_resource.main_pipeline]
}

# Output values
output "bucket_name" {
  description = "The name of the GCS bucket"
  value       = google_storage_bucket.bucket.name
}

output "dataset_id" {
  description = "The ID of the BigQuery dataset"
  value       = google_bigquery_dataset.dataset.dataset_id
}