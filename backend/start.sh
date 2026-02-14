#!/bin/bash

# Adicionar o diretório atual ao PYTHONPATH para garantir que os módulos são encontrados
export PYTHONPATH=$PYTHONPATH:.

# Correr a aplicação FastAPI usando poetry, aceitando ligações IPv6 (::)
poetry run uvicorn main:app --reload --host :: --port 8000
