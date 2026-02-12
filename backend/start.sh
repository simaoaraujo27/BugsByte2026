#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the FastAPI application
uvicorn main:app --reload --host 0.0.0.0 --port 8000