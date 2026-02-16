#!/bin/bash

# Adicionar o diretório atual ao PYTHONPATH para garantir que os módulos são encontrados
export PYTHONPATH=$PYTHONPATH:.

# Produção: respeitar PORT do provider (ex.: Render) e não usar --reload.
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

if [ "${UVICORN_RELOAD:-0}" = "1" ]; then
  poetry run uvicorn main:app --reload --host "$HOST" --port "$PORT"
else
  poetry run uvicorn main:app --host "$HOST" --port "$PORT"
fi
