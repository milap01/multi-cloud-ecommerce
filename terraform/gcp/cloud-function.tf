resource "google_storage_bucket" "code_bucket" {
  name          = "${var.project_id}-function-code"
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket_object" "function_zip" {
  name   = "analytics-function.zip"
  bucket = google_storage_bucket.code_bucket.name
  source = "${path.module}/analytics-function.zip"
}

resource "google_cloudfunctions_function" "analytics_fn" {
  name        = "analytics-function"
  description = "Consumes events and inserts into BigQuery"
  runtime     = "python311"
  entry_point = "main"

  available_memory_mb = 256
  timeout             = 60

  source_archive_bucket = google_storage_bucket.code_bucket.name
  source_archive_object = google_storage_bucket_object.function_zip.name
  event_trigger {
  event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
  resource   = google_pubsub_topic.analytics_topic.name
}


  environment_variables = {
    BIGQUERY_DATASET = google_bigquery_dataset.analytics.dataset_id
    BIGQUERY_TABLE   = google_bigquery_table.events.table_id
  }
}
