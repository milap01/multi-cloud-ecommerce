# Security group for MSK
resource "aws_security_group" "msk" {
  name        = "mce-msk-sg-${var.project_suffix}"
  description = "MSK brokers SG"
  vpc_id      = aws_vpc.main.id

  # allow TLS from VPC (restrict later)
  ingress {
    from_port   = 9094
    to_port     = 9094
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_msk_cluster" "kafka" {
  cluster_name           = "mce-msk-${var.project_suffix}"
  kafka_version          = "3.6.0"
  number_of_broker_nodes = length(aws_subnet.private)

  broker_node_group_info {
    instance_type   = "kafka.t3.small"
    client_subnets  = aws_subnet.private[*].id
    security_groups = [aws_security_group.msk.id]

    storage_info {
      ebs_storage_info {
        volume_size = 20
      }
    }
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }

  tags = { Project = var.project_suffix }
}

