FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_FROZEN=1 \
    UV_NO_SYNC=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

RUN pip install --no-cache-dir uv \
    && groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY . .

USER 1000:1000
EXPOSE 8000
CMD ["python", "-m", "bin.start"]
