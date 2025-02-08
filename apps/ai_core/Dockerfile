FROM python:3.10
# FROM public.ecr.aws/lambda/python:3.10

WORKDIR /app

COPY apps/ai_core /app/apps/ai_core
COPY packages/auth /app/packages/auth
COPY packages/database /app/packages/database
COPY packages/queues /app/packages/queues

RUN pip install --upgrade pip

RUN pip install -e apps/ai_core \
    && pip install -e packages/auth \
    && pip install -e packages/database \
    && pip install -e packages/queues

WORKDIR /app/apps/ai_core

EXPOSE 8001

CMD ["python", "src/ai_core/pipeline.py"]
