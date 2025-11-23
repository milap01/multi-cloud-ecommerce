# Multi-Cloud E-Commerce Platform
## System Design Document

**Project:** Cloud Computing Assignment - Multi-Cloud Microservices Architecture  
**Course:** CS/SS G527 - Cloud Computing  
**Institution:** BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE, PILANI

---

## 1. Executive Summary

This document describes the architecture and design of a production-grade, multi-cloud e-commerce platform built using modern cloud-native technologies. The system leverages **AWS** as the primary cloud provider for core microservices and **Azure** for analytics workloads, demonstrating true multi-cloud architecture principles.

### Key Highlights
- **6+ Microservices:** Frontend, Product, Cart, Order, Search, Events Producer, Analytics Consumer
- **Multi-Cloud:** AWS (EKS, RDS, MSK, DynamoDB, OpenSearch, S3, Lambda) + Azure (Event Hubs, Functions)
- **Infrastructure as Code:** 100% provisioned via Terraform
- **GitOps:** ArgoCD for automated Kubernetes deployments
- **Observability:** Prometheus, Grafana, Loki stack
- **Stream Processing:** Apache Flink for real-time analytics
- **Auto-scaling:** Horizontal Pod Autoscalers (HPA) for critical services

---

## 2. System Overview

### 2.1 Business Context
The platform implements a scalable e-commerce system supporting:
- Product catalog management
- Shopping cart functionality
- Order processing with event-driven workflows
- Real-time product search
- Stream analytics for user behavior tracking
- Asynchronous image processing

### 2.2 Architecture Principles
1. **Microservices Architecture:** Loosely coupled services with clear boundaries
2. **Cloud-Native:** Kubernetes-native, containerized workloads
3. **Event-Driven:** Kafka-based asynchronous communication
4. **Multi-Cloud:** Strategic service placement across AWS and Azure
5. **Infrastructure as Code:** Declarative, version-controlled infrastructure
6. **GitOps:** Git as single source of truth for deployments
7. **Observability-First:** Comprehensive monitoring and logging

---

## 3. Cloud Deployment Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud (Primary)                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              EKS Cluster (Kubernetes)                     │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │ Frontend │  │ Product  │  │   Cart   │  │  Order   │ │  │
│  │  │ (LoadB)  │  │ Service  │  │ Service  │  │ Service  │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  │  ┌──────────┐  ┌──────────┐                              │  │
│  │  │  Search  │  │  Events  │                              │  │
│  │  │ Service  │  │ Producer │                              │  │
│  │  └──────────┘  └──────────┘                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│  ┌────────────┬───────────┴──────────┬───────────┬──────────┐  │
│  │   RDS      │    MSK Kafka         │ DynamoDB  │OpenSearch│  │
│  │ (Postgres) │  (Event Stream)      │  (Cart)   │ (Search) │  │
│  └────────────┴──────────────────────┴───────────┴──────────┘  │
│                                                                   │
│  ┌──────────────────────┐          ┌────────────────────────┐  │
│  │   S3 Bucket          │──────────│  Lambda Function       │  │
│  │  (File Uploads)      │  trigger │  (Image Processor)     │  │
│  └──────────────────────┘          └────────────────────────┘  │
└───────────────────────────────┬───────────────────────────────┘
                                │ Event Bridge
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Azure Cloud (Analytics)                     │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Event Hubs (Kafka Protocol)                  │  │
│  │  Topics: events (input), results (output)                 │  │
│  └───────────────┬─────────────────────┬────────────────────┘  │
│                  │                     │                         │
│       ┌──────────▼─────────┐  ┌───────▼──────────────┐         │
│       │  Flink Job         │  │ Azure Function       │         │
│       │  (HDInsight/AKS)   │  │ (Analytics Consumer) │         │
│       │  - Unique users    │  │ - Read results       │         │
│       │  - 1-min windows   │  │ - Store/expose       │         │
│       └────────────────────┘  └──────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Network Architecture

**AWS VPC Configuration:**
- **CIDR:** 10.0.0.0/16
- **Public Subnets:** 2 subnets across AZs (for NAT Gateway, Load Balancers)
- **Private Subnets:** 2 subnets across AZs (for EKS nodes, RDS, MSK, OpenSearch)
- **NAT Gateway:** Single NAT in first public subnet for private subnet internet access
- **VPC Endpoints:** S3, ECR API/DKR, CloudWatch Logs, STS, EKS API (private connectivity)

**Security Groups:**
- **EKS Cluster SG:** Control plane communication
- **EKS Node SG:** Node-to-node, cluster-to-node communication
- **RDS SG:** PostgreSQL (5432) from VPC CIDR
- **MSK SG:** Kafka (9092/9094) from VPC CIDR
- **OpenSearch SG:** HTTPS (443) from VPC CIDR
- **VPC Endpoints SG:** HTTPS (443) from VPC CIDR

---

## 4. Microservices Architecture

### 4.1 Service Catalog

| Service | Purpose | Language | Database | Port | HPA | Cloud |
|---------|---------|----------|----------|------|-----|-------|
| **Frontend** | Web UI, API Gateway | Python/FastAPI | - | 8000 | ✓ | AWS EKS |
| **Product** | Catalog management | Python/FastAPI | RDS Postgres | 8000 | ✓ | AWS EKS |
| **Cart** | Shopping cart | Python/FastAPI | DynamoDB | 8000 | ✓ | AWS EKS |
| **Order** | Order processing | Python/FastAPI | RDS Postgres | 8000 | ✓ | AWS EKS |
| **Search** | Product search | Python/FastAPI | OpenSearch | 8000 | ✓ | AWS EKS |
| **Events Producer** | Event generation | Python/FastAPI | Kafka/MSK | 8000 | ✓ | AWS EKS |
| **Analytics Consumer** | Results consumer | Python/Flask | Azure Event Hubs | 8000 | - | AWS EKS |
| **Flink Job** | Stream processing | Python/PyFlink | Event Hubs | - | - | Azure |
| **Lambda** | Image processor | Python | S3 | - | - | AWS |

### 4.2 Service Details

#### 4.2.1 Frontend Service
**Responsibility:**
- Serves as the main entry point for users
- Aggregates data from backend microservices
- Handles HTTP routing and request orchestration

**Technology Stack:**
- FastAPI for async request handling
- HTTPx for service-to-service communication
- Exposed via Kubernetes LoadBalancer

**Interactions:**
- Calls Product Service for catalog data
- Calls Cart Service for shopping cart operations
- Calls Order Service for checkout
- Calls Search Service for product queries

**Deployment:**
- Min replicas: 2, Max replicas: 10
- HPA based on CPU (60% threshold)
- Resource requests: 200m CPU, 256Mi memory

#### 4.2.2 Product Service
**Responsibility:**
- Manages product catalog (CRUD operations)
- Provides product details and listings
- Publishes product events to Kafka

**Technology Stack:**
- FastAPI with psycopg2 for PostgreSQL connectivity
- Confluent Kafka client for event publishing

**Database Schema (RDS PostgreSQL):**
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Interactions:**
- Reads/writes to RDS PostgreSQL
- Publishes product change events to MSK Kafka
- Called by Frontend, Cart, Order services

**Deployment:**
- Min replicas: 2, Max replicas: 10
- HPA based on CPU (60% threshold)

#### 4.2.3 Cart Service
**Responsibility:**
- Manages user shopping carts
- Handles add/remove/update cart operations
- Session-based cart persistence

**Technology Stack:**
- FastAPI with boto3 for DynamoDB access
- DynamoDB for NoSQL cart storage

**DynamoDB Table:**
- **Table Name:** mce-cart-mce-2
- **Partition Key:** cartId (String)
- **Billing:** PAY_PER_REQUEST (on-demand)

**Data Model:**
```json
{
  "cartId": "user123_session456",
  "userId": "user123",
  "items": [
    {"productId": "prod1", "quantity": 2, "price": 29.99}
  ],
  "total": 59.98,
  "updatedAt": "2025-11-23T10:30:00Z"
}
```

**Interactions:**
- Called by Frontend for cart operations
- Reads product details from Product Service
- Writes cart events to Kafka

**Deployment:**
- Min replicas: 1, Max replicas: 8
- HPA based on CPU (60% threshold)

#### 4.2.4 Order Service
**Responsibility:**
- Processes customer orders
- Manages order lifecycle (created → paid → shipped → delivered)
- Ensures transactional consistency

**Technology Stack:**
- FastAPI with PostgreSQL for order persistence
- Kafka producer for order events

**Database Schema (RDS PostgreSQL):**
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'created',
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL
);
```

**Interactions:**
- Called by Frontend for checkout
- Validates products via Product Service
- Publishes order events to Kafka (orders topic)
- Consumed by downstream analytics

**Deployment:**
- Min replicas: 1, Max replicas: 8
- HPA based on CPU (60% threshold)

#### 4.2.5 Search Service
**Responsibility:**
- Provides full-text search across product catalog
- Indexes product data from Kafka events
- Returns search results with ranking

**Technology Stack:**
- FastAPI with OpenSearch client
- Consumes product events from Kafka to update index

**OpenSearch Configuration:**
- **Domain:** mce-search-mce-2
- **Version:** OpenSearch 3.1
- **Instance Type:** t3.small.search
- **Instance Count:** 2 (multi-AZ)
- **EBS Volume:** 10GB per instance

**Index Mapping:**
```json
{
  "mappings": {
    "properties": {
      "productId": {"type": "keyword"},
      "name": {"type": "text"},
      "description": {"type": "text"},
      "price": {"type": "float"},
      "category": {"type": "keyword"}
    }
  }
}
```

**Deployment:**
- Min replicas: 1, Max replicas: 6
- HPA based on CPU (60% threshold)

#### 4.2.6 Events Producer Service
**Responsibility:**
- Generates synthetic user activity events
- Publishes events to Kafka for analytics pipeline
- Simulates user behavior (views, adds, purchases)

**Event Schema:**
```json
{
  "user_id": "user123",
  "event_type": "view_product",
  "product_id": "prod456",
  "timestamp": 1700752800,
  "metadata": {}
}
```

**Deployment:**
- Single replica (event generator)
- Min replicas: 1, Max replicas: 5

#### 4.2.7 Analytics Consumer Service
**Responsibility:**
- Consumes aggregated analytics results from Azure Event Hubs
- Exposes metrics via HTTP endpoint
- Provides real-time analytics dashboard data

**Technology Stack:**
- Flask web framework
- Azure Event Hubs SDK (azure-eventhub)

**Deployment:**
- Single replica
- Exposes `/metrics` endpoint

#### 4.2.8 Flink Stream Processing Job (Azure)
**Responsibility:**
- Real-time stream processing of user events
- Computes unique users per 1-minute tumbling windows
- Publishes aggregated results back to Event Hubs

**Processing Logic:**
```python
# Pseudocode
events_stream
  .keyBy(lambda e: 1)  # Global aggregation
  .window(TumblingEventTimeWindows.of(Time.minutes(1)))
  .process(UniqueUsersPerWindow())
  .sink_to(results_topic)
```

**Output Schema:**
```json
{
  "window_start": 1700752800000,
  "window_end": 1700752860000,
  "unique_users": 42,
  "event_count": 150
}
```

**Deployment:**
- Runs on Azure HDInsight or AKS
- Connects to Event Hubs via Kafka protocol

#### 4.2.9 Lambda Image Processor (Serverless)
**Responsibility:**
- Triggered by S3 uploads
- Processes uploaded images (resize, thumbnail generation)
- Asynchronous, event-driven execution

**Trigger:** S3 ObjectCreated:* events on `mce-uploads-mce-2` bucket

**Execution:**
- Runtime: Python 3.10
- Memory: 256MB
- Timeout: 60 seconds

---

## 5. Data Architecture

### 5.1 Database Strategy

| Database | Type | Use Case | Rationale |
|----------|------|----------|-----------|
| **RDS PostgreSQL** | Relational | Products, Orders | ACID compliance, complex queries, relationships |
| **DynamoDB** | NoSQL | Shopping Carts | High throughput, low latency, session data |
| **OpenSearch** | Search Engine | Product Search | Full-text search, faceted filtering, relevance ranking |
| **S3** | Object Store | File Uploads | Scalable, durable storage for images/files |

### 5.2 Event Streaming Architecture

**AWS MSK (Managed Kafka):**
- **Cluster:** mce-msk-mce-2
- **Version:** Kafka 3.6.0
- **Brokers:** 2 (multi-AZ)
- **Instance Type:** kafka.t3.small
- **Encryption:** TLS in transit, AWS KMS at rest

**Topics:**
- `user-events`: User activity events
- `orders`: Order lifecycle events
- `products`: Product change events

**Azure Event Hubs:**
- **Namespace:** mce-events-ns-mce
- **Topics:** events (input), results (output)
- **Compatibility:** Kafka protocol enabled
- **Purpose:** Cross-cloud event bridge for analytics

---

## 6. Infrastructure as Code (Terraform)

### 6.1 AWS Resources (terraform/aws/)

**Key Modules:**
- `vpc.tf`: VPC, subnets, NAT, Internet Gateway
- `eks.tf`: EKS cluster using terraform-aws-modules/eks
- `rds.tf`: PostgreSQL RDS instance
- `msk.tf`: Managed Kafka cluster
- `dynamodb.tf`: DynamoDB cart table
- `opensearch.tf`: OpenSearch domain
- `s3_lambda.tf`: S3 bucket + Lambda function + event notifications
- `ecr.tf`: ECR repositories for all microservices
- `endpoints.tf`: VPC endpoints for private AWS service access
- `iam.tf`: IAM roles and policies

**Terraform State:**
- Stored locally (for assignment; production would use S3 backend)
- Sensitive values in variables marked as sensitive

### 6.2 Azure Resources (terraform/azure/)

**Key Modules:**
- `main.tf`: Resource group, VNet
- `aks.tf`: AKS cluster (optional, for Flink)
- `eventhub.tf`: Event Hubs namespace and topics
- `function.tf`: Azure Function App for analytics consumer

---

## 7. GitOps Deployment Strategy

### 7.1 ArgoCD Architecture

**Installation:**
- Deployed in `argocd` namespace
- Server exposed via LoadBalancer
- Admin credentials managed via kubectl secrets

**Project Structure:**
```
gitops/
├── project.yaml              # ArgoCD AppProject definition
├── app-of-apps.yaml          # Root Application (App of Apps pattern)
└── apps/
    ├── frontend.yaml
    ├── product.yaml
    ├── cart.yaml
    ├── order.yaml
    ├── search.yaml
    ├── event-producer.yaml
    ├── analytics-consumer.yaml
    └── stream-processor.yaml
```

**Sync Policy:**
- **Automated:** prune: true, selfHeal: true
- **Source:** GitHub repository (main branch)
- **Path:** k8s/{service-name}

### 7.2 Kubernetes Manifests Structure

```
k8s/
├── namespace.yaml            # mce, observability namespaces
├── configmap-common.yaml     # Shared configuration
├── secret-template.yaml      # Template for secrets
├── frontend/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── product/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
└── observability/
    ├── prometheus/values.yaml
    ├── grafana/values.yaml
    └── service-monitors/*.yaml
```

**ConfigMap (Common):**
```yaml
data:
  AWS_REGION: "us-east-1"
  RDS_HOST: "mce-postgres-mce-2.xxx.rds.amazonaws.com"
  KAFKA_BOOTSTRAP: "b-1.mcemskmce2.xxx:9094,b-2..."
  OPENSEARCH_ENDPOINT: "vpc-mce-search-mce-2.xxx.es.amazonaws.com"
  PRODUCT_SERVICE_URL: "http://product.mce.svc.cluster.local"
```

---

## 8. CI/CD Pipeline

### 8.1 GitHub Actions Workflow

**Trigger:** Push to `main` branch

**Jobs:**
1. **Build & Push Docker Images** (matrix strategy for all services)
   - Checkout repository
   - Configure AWS credentials
   - Login to ECR
   - Build and tag images (`:latest` and `:${SHORT_SHA}`)
   - Push images to ECR

2. **Update Kubernetes Manifests**
   - Patch `k8s/{service}/deployment.yaml` with new image SHA
   - Commit and push changes to Git

3. **ArgoCD Auto-Sync**
   - Detects Git changes
   - Automatically syncs new image tags to cluster
   - Performs rolling update

**Benefits:**
- No manual `kubectl apply`
- Git as single source of truth
- Audit trail of all deployments

---

## 9. Observability Stack

### 9.1 Metrics (Prometheus + Grafana)

**Prometheus:**
- Deployed via kube-prometheus-stack Helm chart
- Scrapes metrics from ServiceMonitors
- Scrape interval: 10 seconds
- Retention: 15 days

**ServiceMonitors:**
- Deployed per microservice in `observability` namespace
- Label selector: `team: mce`
- Targets `/metrics` endpoints on all services

**Grafana:**
- Pre-configured Prometheus datasource
- Custom dashboard: Service Metrics (RPS, error rate, p95 latency)
- Exposed via LoadBalancer

**Key Metrics:**
- `http_requests_total`: Request counter per service
- `http_request_duration_seconds`: Request latency histogram
- `container_cpu_usage_seconds_total`: CPU usage per pod
- `container_memory_working_set_bytes`: Memory usage per pod

### 9.2 Logging (Loki + Promtail)

**Loki:**
- Deployed via Helm chart
- Storage: Filesystem (local for assignment)
- Aggregates logs from all pods

**Promtail:**
- DaemonSet on all nodes
- Collects logs from `/var/log/pods`
- Labels: namespace, pod, container

**Query Example:**
```logql
{namespace="mce", app="frontend"} |= "error" | json
```

---

## 10. Scaling and Performance

### 10.1 Horizontal Pod Autoscaler (HPA)

**Configuration:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    kind: Deployment
    name: frontend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
```

**Services with HPA:**
- Frontend: 2-10 replicas
- Product: 2-10 replicas
- Cart: 1-8 replicas
- Order: 1-8 replicas
- Search: 1-6 replicas
- Events Producer: 1-5 replicas

### 10.2 Load Testing

**Tool:** k6 (JavaScript-based)

**Test Scenario:**
- Ramp up: 30s to 50 users
- Sustained load: 2 minutes at 200 users
- Ramp down: 30s to 0 users

**Endpoints Tested:**
- `GET /products`: List products
- `POST /cart/add`: Add item to cart

**Success Criteria:**
- HPA scales out services during sustained load
- P95 latency < 500ms
- Error rate < 1%

---

## 11. Security Considerations

### 11.1 Network Security
- All EKS nodes in private subnets
- No public IPs on worker nodes
- VPC endpoints for AWS service access (no internet)
- Security groups with least privilege

### 11.2 Secrets Management
- Kubernetes Secrets for sensitive data (DB passwords, API keys)
- AWS IAM roles for service accounts (IRSA) for pod-level permissions
- ECR image scanning enabled

### 11.3 Encryption
- RDS: Encryption at rest (default AWS KMS)
- MSK: TLS in transit, KMS at rest
- EKS: Envelope encryption for secrets (KMS)
- S3: Server-side encryption (SSE-S3)

---

## 12. Rationale for Design Choices

### 12.1 Multi-Cloud Strategy
**AWS (Primary):**
- Mature managed services (EKS, RDS, MSK, OpenSearch)
- Strong ecosystem for microservices
- Cost-effective for compute and storage

**Azure (Analytics):**
- Event Hubs for Kafka-compatible streaming
- Azure Functions for serverless event processing
- Demonstrates multi-cloud data flow

**Rationale:** Avoid vendor lock-in, leverage best-of-breed services

### 12.2 Database Selection
- **RDS PostgreSQL:** ACID transactions for orders, relational integrity for products
- **DynamoDB:** Single-digit millisecond latency for cart operations, auto-scaling
- **OpenSearch:** Specialized for full-text search, faceted filtering

### 12.3 GitOps with ArgoCD
- **Declarative:** Desired state in Git
- **Automated:** Self-healing, automatic sync
- **Auditable:** Git history tracks all changes

### 12.4 Event-Driven Architecture
- **Loose Coupling:** Services communicate via Kafka
- **Scalability:** Event producers/consumers scale independently
- **Resilience:** Message buffering in Kafka during consumer downtime

### 12.5 Observability-First
- **Proactive Monitoring:** Detect issues before users report
- **Root Cause Analysis:** Logs + metrics for debugging
- **Performance Optimization:** Identify bottlenecks via latency metrics

---

## 13. Future Enhancements

1. **Service Mesh (Istio/Linkerd):** mTLS, traffic management, circuit breaking
2. **Distributed Tracing (Jaeger):** Request flow visualization
3. **Multi-Region Deployment:** Active-active for disaster recovery
4. **Cost Optimization:** Spot instances, Reserved Instances, Savings Plans
5. **Advanced Analytics:** Machine learning for recommendations, fraud detection
6. **API Gateway:** Kong/Ambassador for centralized API management

---

## 14. Conclusion

This multi-cloud e-commerce platform demonstrates enterprise-grade cloud-native architecture principles. The system leverages IaC for reproducibility, GitOps for operational excellence, and event-driven patterns for scalability. The strategic use of AWS and Azure showcases the ability to architect across cloud providers while maintaining operational consistency.

**Key Achievements:**
✓ 7 microservices deployed across 2 cloud providers  
✓ 100% infrastructure provisioned via Terraform  
✓ GitOps-based deployments with ArgoCD  
✓ Real-time stream processing with Flink  
✓ Comprehensive observability with Prometheus/Grafana/Loki  
✓ Auto-scaling validated via load testing  
✓ Serverless function for asynchronous processing  

---
