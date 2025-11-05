# Lakehouse Project - Instruções de Uso

## 🚀 Mudanças Implementadas

### 1. PostgreSQL para Airflow
- Adicionado serviço PostgreSQL dedicado para armazenar metadados do Airflow
- Configurado com healthcheck para garantir disponibilidade
- Volume persistente para dados do PostgreSQL

### 2. Configuração do Prometheus
- Adicionado volume persistente para dados do Prometheus
- Configurado com parâmetros otimizados para armazenamento
- Restart automático habilitado

### 3. Configuração do Grafana
- Volume persistente para dados do Grafana
- Provisionamento automático de datasources (Prometheus e Loki)
- Plugins pré-instalados
- Dependências corretas com Prometheus e Loki

### 4. Configuração do Loki e Promtail
- Loki configurado com armazenamento em filesystem
- Promtail configurado para coletar logs de containers Docker
- Volumes persistentes para dados do Loki

### 5. Airflow com CeleryExecutor
- Todos os componentes do Airflow configurados para usar CeleryExecutor
- Redis como broker de mensagens
- PostgreSQL como backend de resultados
- Workers separados por camada (bronze, silver, gold)
- Dependências corretas com healthchecks

## 📦 Serviços e Portas

| Serviço | Porta | Credenciais |
|---------|-------|-------------|
| PostgreSQL | 5432 | airflow / airflow |
| Airflow | 8080 | admin / admin |
| Prometheus | 9090 | - |
| Grafana | 3000 | admin / admin |
| Loki | 3100 | - |
| MinIO | 9000, 9001 | minioadmin / minioadmin |
| Kafka UI | 8082 | - |
| Mongo Express | 8081 | - |
| Cassandra | 9042 | - |
| Dremio | 9047 | - |

## 🔧 Como Usar

### 1. Primeiro Deploy (Inicial)

```powershell
# Construir as imagens
docker-compose build

# Subir todos os serviços
docker-compose up -d

# Verificar logs do airflow-init
docker-compose logs -f airflow-init
```

### 2. Acessar Serviços

- **Airflow**: http://localhost:8080
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **MinIO**: http://localhost:9001
- **Kafka UI**: http://localhost:8082

### 3. Configurar Grafana

O Grafana já vem com datasources pré-configurados:
- **Prometheus**: Para métricas
- **Loki**: Para logs

Para criar dashboards:
1. Acesse http://localhost:3000
2. Login: admin / admin
3. Vá em Dashboards > New Dashboard
4. Adicione painéis usando Prometheus ou Loki como fonte

### 4. Monitorar Containers

```powershell
# Ver status de todos os containers
docker-compose ps

# Ver logs de um serviço específico
docker-compose logs -f [nome-do-servico]

# Ver logs do Airflow
docker-compose logs -f airflow-webserver
docker-compose logs -f airflow-scheduler

# Ver logs dos workers
docker-compose logs -f airflow-worker-bronze
docker-compose logs -f airflow-worker-silver
docker-compose logs -f airflow-worker-gold
```

### 5. Parar e Reiniciar

```powershell
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados!)
docker-compose down -v

# Reiniciar um serviço específico
docker-compose restart [nome-do-servico]
```

### 6. Verificar PostgreSQL

```powershell
# Conectar ao PostgreSQL
docker exec -it postgres psql -U airflow -d airflow

# Dentro do psql, listar tabelas
\dt

# Sair
\q
```

## 🐛 Troubleshooting

### Airflow não inicia
```powershell
# Verificar logs do postgres
docker-compose logs postgres

# Verificar logs do airflow-init
docker-compose logs airflow-init

# Recriar o banco de dados
docker-compose down
docker volume rm lakehouse-project_postgres-data
docker-compose up -d
```

### Prometheus não coleta métricas
```powershell
# Verificar configuração
docker exec prometheus cat /etc/prometheus/prometheus.yml

# Verificar targets
# Acesse: http://localhost:9090/targets
```

### Grafana não mostra dados
1. Verifique se os datasources estão configurados em Configuration > Data Sources
2. Teste a conexão com Prometheus
3. Verifique se o Prometheus está coletando dados

## 📊 Volumes Persistentes

Os seguintes dados são persistentes:
- `postgres-data`: Metadados do Airflow
- `prometheus-data`: Métricas do Prometheus
- `grafana-data`: Dashboards e configurações do Grafana
- `loki-data`: Logs do Loki
- `miniodata`: Objetos do MinIO
- `cassandradata`: Dados do Cassandra

## 🔄 Atualizar Configurações

Após modificar arquivos de configuração:

```powershell
# Recarregar configuração do Prometheus
docker-compose restart prometheus

# Recarregar configuração do Grafana
docker-compose restart grafana

# Reconstruir imagens do Airflow
docker-compose build airflow-webserver airflow-scheduler airflow-worker-bronze airflow-worker-silver airflow-worker-gold
docker-compose up -d
```
