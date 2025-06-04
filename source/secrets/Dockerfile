FROM public.ecr.aws/docker/library/python:3.13.3

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user to run the application
RUN useradd -m appuser
USER appuser

# Expose the port the app runs on
EXPOSE 8099

# Command to run the application
CMD ["gunicorn", "secrets_service:app", "-b", "0.0.0.0:8099", "-k", "uvicorn.workers.UvicornWorker"]
