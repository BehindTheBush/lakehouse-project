# dags/bronze/usuarios_bronze.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import os
import json
from minio import Minio
from io import BytesIO
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# Função de ingestão
def fetch_and_store_json(**context):

    execution_date = context["ds"]  # yyyy-mm-dd
    ano = execution_date[:4]  # yyyy
    mes = execution_date[5:7]  # mm
    dia = execution_date[8:10]  # dd
    bucket = "lakehouse"
    object_path = f"bronze/usuarios/ano={ano}/mes={mes}/dia={dia}/usuarios.json"


    url = "https://jsonplaceholder.typicode.com/users"
    response = requests.get(url)
    data = response.json()

    json_bytes = BytesIO(json.dumps(data).encode("utf-8"))

    client = Minio(
        "minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    # Cria bucket se não existir
    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)

    # Envia o arquivo JSON
    client.put_object(
        bucket_name=bucket,
        object_name=object_path,
        data=json_bytes,
        length=len(json_bytes.getvalue()),
        content_type="application/json"
    )
    print(f"Arquivo salvo em: {object_path}")

# DAG
with DAG(
    dag_id="usuarios_bronze",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["bronze"],
) as dag:

    fetch_and_store = PythonOperator(
        task_id="fetch_api_and_save_to_bronze",
        python_callable=fetch_and_store_json,
        provide_context=True,
        queue="bronze",
    )

    trigger_silver = TriggerDagRunOperator(
        task_id="trigger_usuarios_silver",
        trigger_dag_id="usuarios_silver",
        wait_for_completion=False,  # Não espera o fim da silver
    )

    fetch_and_store >> trigger_silver