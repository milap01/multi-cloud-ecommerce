resource "google_dataproc_cluster" "flink_cluster" {
  name   = "mce-flink-cluster"
  region = var.region

  runtime_config {
    version = "2.1" # Supports Flink and Python 3.10+
  }

  cluster_config {
    # Use the existing VPC and Subnet from network.tf
    gce_cluster_config {
      network    = google_compute_network.vpc.name
      subnetwork = google_compute_subnetwork.subnet.name
      
      # OAuth scopes for GCS, logging, etc.
      service_account_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]
    }

    # Master Node Configuration
    master_config {
      num_instances = 1
      machine_type  = "e2-medium"
      disk_config {
        boot_disk_type    = "pd-standard"
        boot_disk_size_gb = 30
      }
    }

    # Worker Node Configuration
    worker_config {
      num_instances = 2
      machine_type  = "e2-medium"
      disk_config {
        boot_disk_type    = "pd-standard"
        boot_disk_size_gb = 30
      }
    }

    # Software Config: Install Flink
    software_config {
      image_version = "2.1-debian11"
      optional_components = ["FLINK", "DOCKER"]
    }

    endpoint_config {
      enable_http_port_access = true
    }
  }

  depends_on = [google_compute_subnetwork.subnet]
}

output "dataproc_cluster_name" {
  value = google_dataproc_cluster.flink_cluster.name
}