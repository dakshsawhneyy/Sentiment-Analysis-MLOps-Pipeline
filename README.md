# **Automated Sentiment Analysis MLOps Pipeline**

## **1. Why This Project**

I wanted to build an end-to-end MLOps system that behaves like a real production pipeline — automated ingestion, preprocessing, training, validation, registry updates, serving, monitoring, and infra automation.

---

## **2. What I Wanted to Build**

* A pipeline that **fetches data → cleans → processes → trains → validates → deploys** automatically.
* A system that can **replace old models with better ones** using metrics.
* A setup where **monitoring, autoscaling, and infrastructure** are handled the way real companies do.
* A fully **Docker-based**, **Terraform-provisioned**, **production-grade** deployment.

---

## **3. What I Planned**

* Use **MinIO** as object storage to simulate S3.
* Use **Docker Compose** for all ML components locally.
* Implement **CI/CD** with GitHub Actions.
* Provision infra using **Terraform (EC2 + ASG + ALB)** and launch the entire pipeline using `user-data` scripts.
* Keep model code simple (TF-IDF + Logistic Regression) so the focus stays on MLOps, not ML.

---

## **4. What I Built**

### **Core MLOps Components**

| Component                | Purpose                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------- |
| **Ingestor**             | Fetch raw CSV/JSONL → upload to MinIO `raw/` bucket                                |
| **Processor**            | Clean + transform → upload processed CSV to MinIO `processed/`                     |
| **Trainer**              | Pull processed data → train TF-IDF + Logistic Regression → log to MLflow (DAGsHub) |
| **Validator**            | Compare new model vs production → promote only if better                           |
| **Server (FastAPI)**     | Serve the promoted model with `/predict` & `/metrics`                              |
| **Prometheus & Grafana** | Collect metrics + visual dashboards                                                |
| **MinIO**                | Storage backend for all artifacts                                                  |

### **Infrastructure**

* **Terraform** provisions:

  * VPC + subnets
  * EC2 Auto Scaling Group
  * Application Load Balancer
  * Security groups
  * EC2 launch template with `user-data.sh.tpl`
* EC2 automatically:

  * Clones the repo
  * Writes secrets into `.env`
  * Runs the entire pipeline using Docker Compose

### **CI/CD**

* **CI**

  * Linting
  * Security scans (Trivy and Sonar)
  * Unit imports test
  * Build + push Docker images

* **CD**

  * GitHub Actions → Terraform apply → Infra created
  * Terraform launch template runs Docker Compose automatically

---

## **5. How It Works (End-to-End Flow)**

1. **MinIO stores raw + processed files and model artifacts**
2. **Ingestor** runs → uploads raw `.jsonl`
3. **Processor** converts raw → cleaned CSV
4. **Trainer** trains using MinIO data → logs to DAGsHub MLflow
5. **Validator** promotes the model if metrics improve
6. **Server** loads `production_model.joblib` from MinIO
7. **Prometheus** scrapes FastAPI model metrics
8. **Grafana** shows dashboards
9. **Terraform deployment** runs everything on EC2/ASG/ALB automatically
10. **CI/CD keeps system updated** on every push

---

## **6. Repository Structure**

```
.
├── src
│   ├── ingestor/
│   ├── processor/
│   ├── trainer/
│   ├── validator/
│   └── serving/
├── monitoring/
│   └── prom.yml
├── docker-compose.yml
├── infrastructure/
│   └── main_infra + remote_backend
└── README.md
```

---

## **7. High-Level Architecture**

> **Space reserved for diagram**
> (Infra + pipeline + ALB → ASG → EC2 → Docker Compose → Services)

---

## **8. How to Run Locally**

```
docker compose up -d
```

MinIO → [http://localhost:9001](http://localhost:9001)
FastAPI → [http://localhost:8000](http://localhost:8000)
Prometheus → [http://localhost:9090](http://localhost:9090)
Grafana → [http://localhost:3000](http://localhost:3000)

---

## **9. How to Deploy With Terraform**

Inside `/infrastructure/main_infra`:

```
terraform init
terraform apply
```

Infra comes up → EC2 runs `user-data.sh.tpl` → pipeline starts automatically.

---
