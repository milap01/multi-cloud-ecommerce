resource "google_compute_network" "vpc" {
  name                    = "analytics-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "analytics-subnet"
  ip_cidr_range = "10.50.0.0/16"
  region        = var.region
  network       = google_compute_network.vpc.id
}
