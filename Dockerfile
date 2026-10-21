# The application uses only Python's standard library; test tools stay out of the image.
FROM python:3.12-slim
WORKDIR /app
COPY pipeline.py ./pipeline.py
USER 10001:10001
CMD ["python", "pipeline.py"]
