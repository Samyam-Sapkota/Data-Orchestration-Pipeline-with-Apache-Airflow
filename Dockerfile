FROM apache/airflow:3.1.4

USER airflow
# USER root

RUN pip install --no-cache-dir \
        selenium \
        beautifulsoup4 \
        pandas \
        psycopg2-binary \
        apache-airflow-providers-postgres