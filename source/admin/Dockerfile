FROM public.ecr.aws/docker/library/python:3.13.3

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "admin:app", "-b 0.0.0.0:8000"]