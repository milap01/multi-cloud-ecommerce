resource "google_pubsub_topic" "analytics_topic" {
  name = "analytics-topic"
}

resource "google_pubsub_subscription" "analytics_sub" {
  name  = "analytics-subscription"
  topic = google_pubsub_topic.analytics_topic.name
}
