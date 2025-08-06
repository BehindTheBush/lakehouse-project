#!/bin/sh

echo $USER

sleep 10

kafka-topics --create \
  --bootstrap-server kafka:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic twitter.filmes.raw.v1

echo "Tópico criado com sucesso!"
