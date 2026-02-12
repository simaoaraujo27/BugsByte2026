#!/bin/bash

# Run the FastAPI application using poetry
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --app-dir ..