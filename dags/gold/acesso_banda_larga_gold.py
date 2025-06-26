# dags/gold/acesso_banda_larga_gold.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from minio import Minio
from io import BytesIO
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd

def aggregate_silver_to_gold(**context):
    bucket = "lakehouse"
    silver_prefix = "silver/acesso_banda_larga/"
    gold_prefix = "gold/acesso_banda_larga/"

    client = Minio(
        "minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    # Lista todos arquivos parquet no silver
    objects = client.list_objects(bucket, prefix=silver_prefix, recursive=True)

    dfs = []
    for obj in objects:
        if not obj.object_name.endswith(".parquet"):
            continue

        # Baixa parquet em bytes
        data = client.get_object(bucket, obj.object_name)
        parquet_bytes = data.read()
        data.close()
        data.release_conn()

        # Lê parquet com pyarrow e converte para pandas
        table = pq.read_table(BytesIO(parquet_bytes))
        df = table.to_pandas()
        dfs.append(df)

    # Concatena todos os dataframes
    if len(dfs) == 0:
        print("Nenhum arquivo parquet encontrado no silver para processar.")
        return

    df_all = pd.concat(dfs, ignore_index=True)

    # Agrupa pelos campos solicitados e soma 'Acessos'
    grouped = df_all.groupby(
        ["Ano", "Mês", "Empresa", "Tipo de Uso", "Meio de Acesso", "Código IBGE Município"],
        as_index=False,
        dropna=False
    ).agg({"Acessos": "sum"})

    # Converte para pyarrow Table
    table_gold = pa.Table.from_pandas(grouped)

    # Define caminho do parquet gold
    gold_object_name = f"{gold_prefix}acesso_banda_larga_gold.parquet"

    # Escreve parquet em buffer para upload
    parquet_buffer = BytesIO()
    pq.write_table(table_gold, parquet_buffer)
    parquet_buffer.seek(0)

    # Upload parquet para gold no MinIO
    client.put_object(
        bucket_name=bucket,
        object_name=gold_object_name,
        data=parquet_buffer,
        length=parquet_buffer.getbuffer().nbytes,
        content_type="application/octet-stream"
    )

with DAG(
    dag_id="acesso_banda_larga_gold",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["gold"],
) as dag:

    gold = PythonOperator(
        task_id="aggregate_silver_to_gold",
        python_callable=aggregate_silver_to_gold,
        provide_context=True,
        queue="gold",
    )
