"""Run migrations, API and the service worker under one container lifecycle."""

import os
import signal
import subprocess
import sys
import time


def configure_environment() -> None:
    connection = os.environ.get("POSTGRES_CONNECTION_STRING")
    if connection and "DATABASE_URL" not in os.environ:
        for scheme in ("postgres://", "postgresql://"):
            if connection.startswith(scheme):
                connection = "postgresql+asyncpg://" + connection[len(scheme) :]
                break
        os.environ["DATABASE_URL"] = connection
    if "KAFKA_BROKERS" in os.environ:
        os.environ.setdefault("KAFKA_BOOTSTRAP_SERVERS", os.environ["KAFKA_BROKERS"])
    database = os.environ.get("POSTGRES_DATABASE_NAME", "")
    if database.endswith("-ad-service-postgres"):
        namespace = database.removesuffix("-ad-service-postgres")
        namespace = namespace.replace("_", "-") + "-auth-service"
        os.environ.setdefault(
            "AUTH_SERVICE_URL", f"http://{namespace}-web.{namespace}.svc:8000"
        )


def main() -> None:
    configure_environment()
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
    commands = [
        [
            sys.executable,
            "-m",
            "uvicorn",
            "bin.api:app",
            "--host",
            "0.0.0.0",
            "--port",
            os.environ.get("PORT", "8000"),
        ]
    ]
    commands.append([sys.executable, "-m", "bin.consumer"])
    children = []
    stopping = False

    def stop(signum, frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    exit_code = 0
    try:
        for command in commands:
            children.append(subprocess.Popen(command))
        while not stopping:
            for child in children:
                code = child.poll()
                if code is not None:
                    exit_code = code if code != 0 else 1
                    stopping = True
                    break
            if not stopping:
                time.sleep(0.2)
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
