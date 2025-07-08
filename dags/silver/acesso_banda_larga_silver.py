# dags/silver/acesso_banda_larga_silver.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from minio import Minio
from io import BytesIO
import pyarrow.csv as pv
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


def faixa_velocidade(v):
    if pd.isna(v):
        return None
    try:
        v = float(v)
    except:
        return None
    if v <= 30:
        return "Básica"
    elif 31 <= v <= 100:
        return "Intermediária"
    elif 101 <= v <= 300:
        return "Avançada"
    else:
        return "Ultra"

def faixa_velocidade_numerica(v):
    if pd.isna(v):
        return None
    try:
        v = float(v)
    except:
        return None
    if v <= 30:
        return 1
    elif 31 <= v <= 100:
        return 2
    elif 101 <= v <= 300:
        return 3
    else:
        return 4


def process_csv_minio_to_silver(**context):
    bucket = "lakehouse"
    bronze_prefix = "bronze/acesso_banda_larga/"
    silver_prefix = "silver/acesso_banda_larga/"

    client = Minio(
        "minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    # Lista os arquivos CSV no bronze
    objects = client.list_objects(bucket, prefix=bronze_prefix, recursive=True)
    
    dfs = []

    for obj in objects:
        if not obj.object_name.endswith(".csv"):
            continue
        
        # Pega o objeto CSV do MinIO
        data = client.get_object(bucket, obj.object_name)
        csv_bytes = data.read()
        data.close()
        data.release_conn()

        # Lê CSV com pyarrow selecionando colunas
        read_options = pv.ReadOptions(use_threads=True)
        parse_options = pv.ParseOptions(delimiter=';')
        convert_options = pv.ConvertOptions(include_columns=["Ano", "Mês", "Empresa", "Velocidade", "Meio de Acesso", "Código IBGE Município", "Acessos"])
        table = pv.read_csv(BytesIO(csv_bytes), read_options=read_options, convert_options=convert_options, parse_options=parse_options)

        # Converte para pandas
        df = table.to_pandas()
        
        df["Velocidade"] = df["Velocidade"].astype(str).str.replace(',', '.').astype(float)
        df["Acessos"] = df["Acessos"].astype(str).str.replace(',', '.').astype(float)
        # Filtra empresas
        empresas_validas = ["TIM", "VIVO", "CLARO", "ALGAR (CTBC TELECOM)"]
        df = df[df["Empresa"].isin(empresas_validas)]

        # Renomeia 'ALGAR (CTBC TELECOM)' para 'ALGAR'
        df["Empresa"] = df["Empresa"].replace({"ALGAR (CTBC TELECOM)": "ALGAR"})
        
        # Cria coluna 'Tipo de Uso'
        df["Tipo de Uso"] = df["Velocidade"].apply(faixa_velocidade)
        df["Ordem Tipo de Uso"] = df["Velocidade"].apply(faixa_velocidade_numerica)
        dfs.append(df)


    if dfs:
        # Concatena todos os dataframes
        df = pd.concat(dfs, ignore_index=True)

        # Converte para pyarrow Table para salvar parquet
        table_silver = pa.Table.from_pandas(df)

        # Define caminho do parquet silver substituindo prefixo bronze
        silver_object_name = obj.object_name.replace(bronze_prefix, silver_prefix).replace(".csv", ".parquet")

        # Escreve parquet em buffer para upload
        parquet_buffer = BytesIO()
        pq.write_table(table_silver, parquet_buffer)
        parquet_buffer.seek(0)

        # Upload parquet para silver no MinIO
        client.put_object(
            bucket_name=bucket,
            object_name=silver_object_name,
            data=parquet_buffer,
            length=parquet_buffer.getbuffer().nbytes,
            content_type="application/octet-stream"
        )

            

# DAG
with DAG(
    dag_id="acesso_banda_larga_silver",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["silver"],
) as dag:

    silver = PythonOperator(
        task_id="process_csv_minio_to_silver",
        python_callable=process_csv_minio_to_silver,
        provide_context=True,
        queue="silver",
    )

    trigger_gold = TriggerDagRunOperator(
        task_id="trigger_acesso_banda_larga_gold",
        trigger_dag_id="acesso_banda_larga_gold",
        wait_for_completion=False, 
    )

    silver >> trigger_gold