FROM node:22-slim AS frontend-builder

WORKDIR /app/frontend

RUN corepack enable && corepack install --global pnpm@10.33.4

COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY frontend/ ./
ARG VITE_BACKEND_API=/api
ENV VITE_BACKEND_API=${VITE_BACKEND_API}
RUN pnpm run build


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY backend/ ./
COPY --from=frontend-builder /app/frontend/dist /app/frontend-dist

RUN mkdir -p /app/backend/data

VOLUME ["/app/backend/data"]

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "300", "app:app"]