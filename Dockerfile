FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . /app/

# Create conda environment
RUN conda env create -f environment.yml

# Set PYTHONPATH
ENV PYTHONPATH=/app/src

# Ensure conda env is used by default
SHELL ["conda", "run", "-n", "teiko_dashboard", "/bin/bash", "-c"]

# Expose FastAPI port
EXPOSE 8000

# Default command: Run data load script, then launch FastAPI
CMD ["bash", "-c", "conda run --no-capture-output -n teiko_dashboard python scripts/create_schema_and_load_data.py && conda run --no-capture-output -n teiko_dashboard uvicorn rest.service:app --host 0.0.0.0 --port 8000"]
