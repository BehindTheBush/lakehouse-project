FROM apache/airflow:2.9.1-python3.10

USER root

# Atualiza pacotes e instala dependências comuns para Airflow e drivers extras
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        python3-dev \
        libpq-dev \
        default-libmysqlclient-dev \
        libsasl2-dev \
        libldap2-dev \
        libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
