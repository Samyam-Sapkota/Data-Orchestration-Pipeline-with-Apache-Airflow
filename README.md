# Data-Orchestration-Docker-Pipeline-with-Apache-Airflow

A full **ETL pipeline** that scrapes data from a real-world **dynamic website using Selenium**, processes it, and loads the cleaned data into **PostgreSQL**, all orchestrated using **Apache Airflow** running inside **Docker**.  
The pipeline is fully automated, schedulable, and provides detailed task-level logging and failure reporting.

---

## Tech Stack

- **Apache Airflow**: 3.1.4  
- **PostgreSQL**: 16  
- **Docker & Docker Compose**
- **Python (Pandas, Selenium, SQLAlchemy)**

---

## Setup Steps (Linux)

> ⚠️ **Windows users**: It is recommended to use **WSL2 (Ubuntu)** for a smooth Docker + Airflow experience.

---

## 1. Clone the Repository

```bash
git clone https://github.com/Samyam-Sapkota/Data-Orchestration-Pipeline-with-Apache-Airflow.git
cd Data-Orchestration-Pipeline-with-Apache-Airflow
```
---

## 2. Create .env File for Airflow Permissions

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

### (Optionally) Verify:
```bash
cat .env
```
### Expected output: AIRFLOW_UID=1000
---

## 3. Initialize Airflow (First Time Only)
### This initializes the Airflow metadata database and pulls required Docker images.

```bash
docker-compose up airflow-init
```
### Wait until you see:
```bash
Airflow initialization completed
```
---
## 4. Start All Airflow Services 
```bash
docker-compose up -d
```
### Verify Containers:
```bash
docker ps
```

---

## 5. Access Airflow Web UI 
### Open browser and go to:

```bash
localhost:8080
```
### Default Credentials:
```bash
Username: airflow
Password: airflow
```
---

## 6. Create PostgreSQL Connection in Airflow
### Navigate inside Airflow UI:
```bash
Admin → Connections → + Add Connection
```
### Fill the fields exactly as below:
```bash

| Field           | Value            |
| --------------- | ---------------- |
| Connection Id   | postgres_default |
| Connection Type | Postgres         |
| Host            | postgres         |
| Login           | airflow          |
| Password        | airflow          |
| Port            | 5432             |
| Database        | airflow          |


```
### Click Save

---

### 7. Trigger the ETL DAG
### i. Go to DAGs
### ii. Search for following dag or choose your own dag if any created:
```bash
Daraz_ETL_dag
```
### Click the DAG
### Click Trigger DAG ▶
#### After some times ,you should see: 
### All tasks turning blue -> green
### DAG state : Success

---

## 8. Verify Data in PostgreSQL 
### Option 1 :  Exec into PostgreSQL Container
```bash
docker ps
```

### Copy the PostgreSQL container name, then:

```bash
docker exec -it <postgres_container_name> psql -U airflow -d airflow
```
---
### Option 2: Run SQL Queries (in any postgres platform)

```bash
SELECT COUNT(*) FROM products;
```
OR
```bash
SELECT * FROM products LIMIT 5;
```
---

## 9. Customization

```bash
dags/
├── extract/
├── transform/
├── load/
```
### You can:
- *Modify existing DAGs*
- *Add new extract / transform / load logic*
- *Connect other databases*
- *Add scheduling, retries, alerts*
 
---

### Notes:
- Airflow runs fully inside Docker
- PostgreSQL runs as a Docker service
- DAGs are auto-loaded from dags/
- Selenium runs using Dockerized Chrome



