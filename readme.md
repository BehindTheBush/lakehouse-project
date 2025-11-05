# 🏗️ Lakehouse Project

> Plataforma completa de Data Lakehouse com orquestração Apache Airflow, streaming Kafka, armazenamento MinIO, processamento Dremio e monitoramento integrado com Prometheus/Grafana.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Tecnologias](#-tecnologias)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Serviços e Portas](#-serviços-e-portas)
- [Uso](#-uso)
- [Camadas do Lakehouse](#-camadas-do-lakehouse)
- [Monitoramento](#-monitoramento)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Troubleshooting](#-troubleshooting)
- [Manutenção](#-manutenção)

---

## 🎯 Visão Geral

Este projeto implementa uma arquitetura moderna de **Data Lakehouse** combinando as melhores práticas de Data Lake e Data Warehouse. A plataforma oferece:

- **Orquestração de Pipelines**: Apache Airflow com CeleryExecutor e workers dedicados por camada
- **Ingestão de Dados em Tempo Real**: Apache Kafka para streaming
- **Armazenamento Object Storage**: MinIO compatível com S3
- **Processamento Analítico**: Dremio para query engine
- **Armazenamento Estruturado**: PostgreSQL, MongoDB, Cassandra
- **Monitoramento Completo**: Prometheus, Grafana, Loki, Promtail
- **Observabilidade**: cAdvisor para métricas de containers, exporters para databases

### Arquitetura em Camadas (Medallion)

O projeto segue o padrão **Medallion Architecture**:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Bronze    │───▶│   Silver    │───▶│    Gold     │
│  (Raw Data) │    │ (Cleaned)   │    │ (Aggregated)│
└─────────────┘    └─────────────┘    └─────────────┘
      ▲                  ▲                   ▲
      │                  │                   │
  Worker Bronze     Worker Silver      Worker Gold
```

---

## 🏛️ Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                    MONITORING LAYER                          │
│  Prometheus │ Grafana │ Loki │ Promtail │ cAdvisor          │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                         │
│  Airflow Webserver │ Scheduler │ Workers (Bronze/Silver/Gold)│
│  Redis (Broker) │ PostgreSQL (Metadata)                      │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                          │
│  Dremio (Query Engine) │ Kafka (Streaming)                   │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                             │
│  MinIO (Object Storage) │ MongoDB │ Cassandra │ PostgreSQL   │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologias

### Orquestração
- **Apache Airflow 2.9.1**: Orquestrador de workflows com DAGs Python
- **Celery**: Executor distribuído para processamento paralelo
- **Redis 7**: Message broker para Celery

### Processamento
- **Apache Kafka 7.5.0**: Plataforma de streaming de eventos
- **Dremio**: Query engine para data lakehouse
- **Zookeeper**: Coordenação do Kafka cluster

### Armazenamento
- **MinIO**: Object storage compatível com S3
- **PostgreSQL 15**: Banco relacional para metadados do Airflow
- **MongoDB**: Banco NoSQL orientado a documentos
- **Cassandra 4**: Banco NoSQL distribuído wide-column

### Monitoramento
- **Prometheus**: Sistema de monitoramento e alertas
- **Grafana**: Visualização de métricas e logs
- **Loki**: Agregação de logs
- **Promtail**: Agent de coleta de logs
- **cAdvisor**: Métricas de containers
- **Exporters**: MongoDB e Cassandra exporters

### UI & Ferramentas
- **Kafka UI**: Interface web para gerenciamento Kafka
- **Mongo Express**: Interface web para MongoDB
- **MinIO Console**: Interface web para object storage

---

## 📦 Pré-requisitos

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git**
- **Sistema Operacional**: Windows, macOS ou Linux
- **Recursos Mínimos**:
  - 8 GB RAM (recomendado 16 GB)
  - 20 GB espaço em disco
  - CPU com 4+ cores

---

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/BehindTheBush/lakehouse-project.git
cd lakehouse-project
```

### 2. Configuração Inicial

A configuração padrão já está pronta para uso. Se necessário, ajuste variáveis de ambiente no `docker-compose.yml`.

### 3. Build e Deploy

```bash
# Build das imagens customizadas
docker-compose build

# Subir todos os serviços
docker-compose up -d

# Acompanhar logs (opcional)
docker-compose logs -f
```

### 4. Verificar Status

```bash
# Verificar containers rodando
docker-compose ps

# Verificar logs do Airflow init
docker-compose logs airflow-init

# Verificar saúde do PostgreSQL
docker-compose logs postgres
```

### 5. Acessar Serviços

Aguarde ~2 minutos para todos os serviços inicializarem completamente, então acesse as interfaces web listadas abaixo.

---

## 🌐 Serviços e Portas

| Serviço           | URL/Host                                        | Credenciais              | Descrição                          |
|-------------------|-------------------------------------------------|--------------------------|------------------------------------|
| **Airflow**       | [http://localhost:8080](http://localhost:8080)  | admin / admin            | Orquestrador de workflows          |
| **Grafana**       | [http://localhost:3000](http://localhost:3000)  | admin / admin            | Dashboards e visualização          |
| **Prometheus**    | [http://localhost:9090](http://localhost:9090)  | —                        | Métricas e alertas                 |
| **MinIO Console** | [http://localhost:9001](http://localhost:9001)  | minioadmin / minioadmin  | Object storage console             |
| **MinIO API**     | `localhost:9000`                                | minioadmin / minioadmin  | API S3-compatible                  |
| **Dremio**        | [http://localhost:9047](http://localhost:9047)  | admin / admin (1º acesso)| Query engine                       |
| **Kafka UI**      | [http://localhost:8082](http://localhost:8082)  | —                        | Interface Kafka                    |
| **Mongo Express** | [http://localhost:8081](http://localhost:8081)  | —                        | Interface MongoDB                  |
| **cAdvisor**      | [http://localhost:8083](http://localhost:8083)  | —                        | Métricas de containers             |
| **Loki**          | `http://localhost:3100`                         | —                        | API de logs                        |
| **PostgreSQL**    | `localhost:5432`                                | airflow / airflow        | Metadados Airflow                  |
| **MongoDB**       | `localhost:27017`                               | root / root              | Banco NoSQL                        |
| **Cassandra**     | `localhost:9042`                                | —                        | Banco distribuído                  |
| **Redis**         | `localhost:6379`                                | —                        | Celery broker                      |
| **Kafka**         | `localhost:9092`                                | —                        | Message broker                     |
| **Zookeeper**     | `localhost:2181`                                | —                        | Kafka coordinator                  |

---

## 💼 Uso

### Gerenciamento de DAGs no Airflow

1. **Acessar Airflow**: http://localhost:8080
2. **Criar DAGs**: Adicionar arquivos `.py` em `dags/bronze/`, `dags/silver/` ou `dags/gold/`
3. **Filas de Execução**:
   - `bronze`: Workers para ingestão de dados brutos
   - `silver`: Workers para limpeza e transformação
   - `gold`: Workers para agregação e analytics

**Exemplo de DAG com fila específica**:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG(
    'exemplo_bronze',
    start_date=datetime(2025, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:
    
    task = PythonOperator(
        task_id='ingest_data',
        python_callable=my_function,
        queue='bronze'  # Define a fila
    )
```

### Monitorar Pipelines

```bash
# Ver logs de um worker específico
docker-compose logs -f airflow-worker-bronze-2

# Ver status do scheduler
docker-compose logs -f airflow-scheduler

# Ver tasks em execução
docker exec airflow-webserver airflow tasks list <dag_id>
```

### Trabalhar com MinIO (Object Storage)

```python
from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Criar bucket
client.make_bucket("bronze-data")

# Upload arquivo
client.fput_object("bronze-data", "file.csv", "/path/to/file.csv")
```

### Streaming com Kafka

```bash
# Produzir mensagens (exemplo)
docker exec -it kafka kafka-console-producer \
  --broker-list localhost:9092 \
  --topic twitter.filmes.raw.v1

# Consumir mensagens
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic twitter.filmes.raw.v1 \
  --from-beginning
```

---

## 🏅 Camadas do Lakehouse

### Bronze (Raw)
- **Propósito**: Ingestão de dados brutos sem transformações
- **Worker**: `airflow-worker-bronze-2`
- **DAGs**: `dags/bronze/`
- **Exemplo**: `usuario_bronze.py`

### Silver (Cleaned)
- **Propósito**: Limpeza, validação e enriquecimento
- **Worker**: `airflow-worker-silver-2`
- **DAGs**: `dags/silver/`
- **Exemplos**: `usuario_silver.py`, `acesso_banda_larga_silver.py`

### Gold (Analytics)
- **Propósito**: Agregações e modelos analíticos
- **Worker**: `airflow-worker-gold-2`
- **DAGs**: `dags/gold/`
- **Exemplo**: `acesso_banda_larga_gold.py`

---

## 📊 Monitoramento

### Grafana Dashboards

O projeto inclui dashboard pré-configurado: **Lakehouse Overview**

**Acesso**: http://localhost:3000 → Dashboards → Lakehouse Overview

**Painéis disponíveis**:
- ✅ Airflow service status
- 💻 Container CPU usage
- 💾 Container memory usage
- 🎯 Prometheus targets health

### Prometheus Targets

**Acesso**: http://localhost:9090/targets

Targets monitorados:
- Prometheus (self-monitoring)
- cAdvisor (métricas de containers)
- Airflow
- Kafka
- Redis
- Cassandra (via exporter)
- MongoDB (via exporter)

### Logs com Loki

Logs centralizados acessíveis via Grafana:
1. Acessar Grafana → Explore
2. Selecionar datasource **Loki**
3. Query exemplo: `{job="containerlogs"}`

### Alertas

Configure alertas no Grafana para:
- Serviços down
- Uso excessivo de CPU/memória
- Falhas em DAGs do Airflow
- Atrasos em filas do Celery

---

## 📂 Estrutura do Projeto

```
lakehouse-project/
├── dags/                          # DAGs do Airflow
│   ├── bronze/                    # Ingestão de dados brutos
│   │   └── usuario_bronze.py
│   ├── silver/                    # Transformação e limpeza
│   │   ├── usuario_silver.py
│   │   └── acesso_banda_larga_silver.py
│   └── gold/                      # Agregações analíticas
│       └── acesso_banda_larga_gold.py
│
├── infra/                         # Infraestrutura
│   ├── airflow/
│   │   ├── Dockerfile             # Imagem customizada Airflow
│   │   └── requirements.txt       # Dependências Python
│   ├── kafka/
│   │   └── init-topics.sh         # Criação de tópicos
│   └── monitoring/
│       ├── prometheus.yml         # Config Prometheus
│       ├── loki-config.yaml       # Config Loki
│       ├── promtail-config.yaml   # Config Promtail
│       └── grafana/
│           └── provisioning/
│               ├── datasources/   # Datasources automáticos
│               │   └── datasources.yaml
│               └── dashboards/    # Dashboards provisionados
│                   ├── dashboards.yaml
│                   └── lakehouse_overview.json
│
├── docker-compose.yml             # Orquestração completa
└── readme.md                      # Este arquivo
```

---

## 🔧 Troubleshooting

### Airflow não inicia

```bash
# Verificar logs do postgres
docker-compose logs postgres

# Verificar logs do airflow-init
docker-compose logs airflow-init

# Resetar banco de dados (CUIDADO: apaga dados)
docker-compose down -v
docker-compose up -d
```

### Workers não processam tasks

```bash
# Verificar se workers estão rodando
docker-compose ps | grep worker

# Verificar logs de um worker
docker-compose logs -f airflow-worker-bronze-2

# Verificar Redis
docker-compose logs redis

# Reiniciar workers
docker-compose restart airflow-worker-bronze-2 airflow-worker-silver-2 airflow-worker-gold-2
```

### Prometheus não coleta métricas

```bash
# Verificar configuração
docker exec prometheus cat /etc/prometheus/prometheus.yml

# Verificar targets no navegador
# http://localhost:9090/targets

# Reiniciar Prometheus
docker-compose restart prometheus
```

### Grafana não mostra dashboard

```bash
# Verificar provisionamento
docker exec grafana ls -la /etc/grafana/provisioning/dashboards/

# Verificar logs
docker-compose logs grafana | grep -i dashboard

# Forçar reload
docker-compose restart grafana
```

### Kafka não recebe mensagens

```bash
# Verificar Zookeeper
docker-compose logs zookeeper

# Verificar Kafka
docker-compose logs kafka

# Listar tópicos
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Descrever tópico
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic twitter.filmes.raw.v1
```

### MinIO inacessível

```bash
# Verificar logs
docker-compose logs minio

# Verificar volumes
docker volume ls | grep minio

# Reiniciar MinIO
docker-compose restart minio
```

### Containers com erro "Out of Memory"

```bash
# Verificar uso de memória
docker stats

# Aumentar recursos no Docker Desktop:
# Settings → Resources → Memory → 8GB+

# Parar serviços não essenciais temporariamente
docker-compose stop mongo mongo-express
```

### Portas já em uso

```bash
# Windows: Verificar porta ocupada
netstat -ano | findstr :8080

# Matar processo (PowerShell como Admin)
Stop-Process -Id <PID> -Force

# Ou alterar porta no docker-compose.yml
# Exemplo: - "8081:8080"  # Expõe na porta 8081
```

---

## 🔄 Manutenção

### Backup de Dados

```bash
# Backup PostgreSQL
docker exec postgres pg_dump -U airflow airflow > backup_airflow.sql

# Backup MongoDB
docker exec mongo mongodump --out /backup

# Backup volumes Docker
docker run --rm -v lakehouse-project_postgres-data:/data -v $(pwd):/backup busybox tar czf /backup/postgres-backup.tar.gz /data
```

### Limpeza de Recursos

```bash
# Remover containers parados
docker-compose down

# Remover volumes (ATENÇÃO: perde dados)
docker-compose down -v

# Limpar imagens não usadas
docker image prune -a

# Limpar tudo do Docker
docker system prune -a --volumes
```

### Atualização de Serviços

```bash
# Atualizar imagem específica
docker-compose pull <service-name>
docker-compose up -d <service-name>

# Rebuild após mudanças no Dockerfile
docker-compose build --no-cache airflow-webserver
docker-compose up -d airflow-webserver

# Atualizar todos os serviços
docker-compose pull
docker-compose up -d --build
```

### Logs e Debugging

```bash
# Todos os logs
docker-compose logs

# Logs de serviço específico
docker-compose logs -f <service-name>

# Logs com timestamp
docker-compose logs -f --timestamps <service-name>

# Últimas 100 linhas
docker-compose logs --tail=100 <service-name>

# Logs de múltiplos serviços
docker-compose logs -f airflow-webserver airflow-scheduler
```

### Escalar Workers

```bash
# Adicionar mais workers (editar docker-compose.yml)
# Duplicar bloco airflow-worker-bronze-2 com novo nome

# Aplicar mudanças
docker-compose up -d --scale airflow-worker-bronze-2=3
```

### Monitorar Recursos

```bash
# Uso em tempo real
docker stats

# Espaço em disco dos volumes
docker system df -v

# Inspecionar container
docker inspect <container-name>
```

---

## 📝 Notas Importantes

- **Senhas padrão**: Altere as credenciais em produção
- **Volumes persistentes**: Dados sobrevivem a `docker-compose down`
- **Recursos**: Ajuste limites no `docker-compose.yml` se necessário
- **Rede**: Todos os serviços na rede `lakehouse-net`
- **Healthchecks**: PostgreSQL tem healthcheck configurado

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

## 👥 Autores

- **BehindTheBush** - [GitHub](https://github.com/BehindTheBush)

---

## 🙏 Agradecimentos

- Apache Airflow Community
- Confluent Platform (Kafka)
- MinIO Team
- Prometheus & Grafana Labs
- Docker & Docker Compose

---

**🚀 Happy Data Engineering!**
