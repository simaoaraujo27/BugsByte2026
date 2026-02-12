# BugsByte2026

Repositório para a Hackathon Bugsbyte 2026

## Project Overview

This project consists of a Python FastAPI backend with a SQLite database and a Vue.js frontend.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Node.js & npm (or Yarn/pnpm):** Required for the Vue.js frontend.
    *   [Node.js Download](https://nodejs.org/)
*   **Python (3.14.0 recommended):** Required for the FastAPI backend.
    *   It is highly recommended to use a Python version manager like `pyenv` to manage your Python versions.
    *   [pyenv GitHub](https://github.com/pyenv/pyenv)
*   **Poetry:** Python dependency management tool for the backend.
    *   [Poetry Installation](https://python-poetry.org/docs/#installation)
    *   You can install it using: `curl -sSL https://install.python-poetry.org | python -`

## Getting Started

### 1. Backend Setup & Run (FastAPI with Poetry)

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Install Python dependencies using Poetry:**
    This will create a virtual environment (if one doesn't exist) and install all required packages.
    ```bash
    poetry install
    ```

3.  **Run the FastAPI application:**
    ```bash
    ./start.sh
    ```
    The backend will start on `http://localhost:8000`. A `sql_app.db` file will be created in the `backend/` directory upon the first database interaction.

### 2. Frontend Setup & Run (Vue.js)

1.  **Open a new terminal and navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Run the Vue.js development server:**
    ```bash
    ./start.sh
    ```
    The frontend will typically start on `http://localhost:5173`.

## How to Develop

### Backend Development

*   **Dependencies:** Use `poetry add <package-name>` to add new Python dependencies.
*   **Running commands:** Use `poetry run <command>` (e.g., `poetry run python my_script.py`) to execute commands within the Poetry-managed environment.
*   **API Endpoints:** Modify `backend/main.py` to add or change API routes.
*   **Database Models:** Update `backend/models.py` for changes to your database schema.
*   **Data Validation:** Adjust `backend/schemas.py` for request and response data validation.

### Frontend Development

*   **Dependencies:** Use `npm install <package-name>` to add new Node.js dependencies.
*   **Components:** Create and modify Vue components in `frontend/src/components/`.
*   **Views/Pages:** Update `frontend/src/App.vue` or create new views/pages with `vue-router` if your application grows.
*   **API Interaction:** The frontend interacts with the backend at `http://localhost:8000`.

---