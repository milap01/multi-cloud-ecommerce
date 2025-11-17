resource "google_bigquery_dataset" "analytics" {
  dataset_id = "ecommerce_analytics"
  location   = var.region
}

resource "google_bigquery_table" "events" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "events"

  schema = jsonencode([
    {"name":"event_id", "type":"STRING", "mode":"REQUIRED"},
    {"name":"event_type", "type":"STRING", "mode":"REQUIRED"},
    {"name":"timestamp", "type":"TIMESTAMP", "mode":"REQUIRED"},
    {"name":"payload", "type":"STRING", "mode":"NULLABLE"}
  ])
}
