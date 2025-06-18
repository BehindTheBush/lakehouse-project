# dags/silver/usuarios_silver.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime
import pandas as pd
from io import BytesIO
from minio import Minio
import pyarrow as pa
import pyarrow.parquet as pq
import json

# Função de transformação
def transform_and_store_parquet(**context):
    execution_date = context["ds"]
    bucket = "lakehouse"
    bronze_path = f"bronze/usuarios/dt={execution_date}/usuarios.json"
    silver_path = f"silver/usuarios/dt={execution_date}/usuarios.parquet"

    # MinIO
    client = Minio(
        "minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    # Lê JSON do Bronze
    response = client.get_object(bucket, bronze_path)
    data = json.loads(response.data.decode("utf-8"))

    # Transforma com Pandas
    df = pd.json_normalize(data)
    table = pa.Table.from_pandas(df)

    # Escreve em Parquet
    parquet_buffer = BytesIO()
    pq.write_table(table, parquet_buffer)

    # Salva no Silver
    client.put_object(
        bucket_name=bucket,
        object_name=silver_path,
        data=BytesIO(parquet_buffer.getvalue()),
        length=len(parquet_buffer.getvalue()),
        content_type="application/octet-stream"
    )
    print(f"Arquivo parquet salvo em: {silver_path}")

# DAG
with DAG(
    dag_id="usuarios_silver",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["silver"],
) as dag:

    espera_bronze = ExternalTaskSensor(
        task_id="espera_bronze_usuarios",
        external_dag_id="usuarios_bronze",
        external_task_id="fetch_api_and_save_to_bronze",
        mode="poke",
        timeout=600,
        poke_interval=30,
    )

    transforma_silver = PythonOperator(
        task_id="transforma_json_para_parquet",
        python_callable=transform_and_store_parquet,
        provide_context=True,
        queue="silver"
    )

    espera_bronze >> transforma_silver
