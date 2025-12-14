# Data-Orchestration-Docker-Pipeline-with-Apache-Airflow
A full ETL pipeline which involves scraping from a real world dynamic site using selenium and loading the preprocessed data to Postgres all in a Airflow Workflow which is automated to schedule and report on errors. 

Airflow Version : 3.1.4 
Postgres Version : 16

<h1> Setup Steps For Linux </h1>  * Use chatgpt for windows with*

1. Clone repo with command :  git clone https://github.com/Samyam-Sapkota/Data-Orchestration-Pipeline-with-Apache-Airflow.git

2. Create a .env file and add line : AIRFLOW_UID=1000   (for me its 1000 on ubuntu so good practice is to use the command echo -e "AIRFLOW_UID=$(id -u)" > .env)

3. Run the below command to initialize airflow internal database and also to trigger Docker to download the required Airflow images if they are not already available on your local machine. :
      docker-compose up airflow-init

4. Once airflow initialized, run the command : docker-compose up -d

5. Airflow UI is now live , visit localhost:8080 then login to the page. Default Credentials : Both Username and password is airflow
    If you get error or server not live at localhost:8080 ,view your port from docker ps command or redo step 4.

6. Once login navigate to admin(left center) -> connections -> add connection . Set followings :
        | Field               | Value                                      |
        | ------------------- | ------------------------------------------ |
        | **Connection Id**   | `postgres_default`                         |
        | **Connection Type** | `Postgres`                                 |
        | **Host**            | `postgres`                                 |
        | **Login**           | `airflow`                                  |
        | **Password**        | `airflow`                                  |
        | **Port**            | `5432`                                     |
        | **Database**        | `airflow` *(database name)*                |

7. 
