resource "google_container_cluster" "gke" {
  name               = "analytics-gke"
  location           = var.region
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.id
  subnetwork = google_compute_subnetwork.subnet.id
}

resource "google_container_node_pool" "primary" {
  name       = "default-node-pool"
  cluster    = google_container_cluster.gke.name
  location   = google_container_cluster.gke.location

  node_count = 1

  node_config {
    machine_type = "e2-small"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
