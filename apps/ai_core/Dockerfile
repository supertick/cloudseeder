FROM public.ecr.aws/lambda/python:3.10

WORKDIR /app

COPY apps/ai_core /app/apps/ai_core

COPY packages/auth /app/packages/auth
COPY packages/database /app/packages/database
COPY packages/queues /app/packages/queues

RUN pip install -e apps/ai_core \
    && pip install -e packages/auth \
    && pip install -e packages/database \
    && pip install -e packages/queues

WORKDIR /app/apps/ai_core

EXPOSE 8001

# RUN chmod +x /app/apps/ai_core/src/ai_core/lambda_function.py
# CMD ["ai_core.lambda_function.lambda_handler"]
# CMD ["uvicorn", "ai_core.main:app", "--host", "0.0.0.0", "--port", "8000"]
ENTRYPOINT ["uvicorn", "ai_core.main:app", "--host", "0.0.0.0", "--port", "8001"]