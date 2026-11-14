from bin.start import configure_environment


def test_platform_environment_mapping(monkeypatch):
    for name in ("DATABASE_URL", "KAFKA_BOOTSTRAP_SERVERS", "AUTH_SERVICE_URL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("POSTGRES_CONNECTION_STRING", "postgres://user:pass@db/test")
    monkeypatch.setenv("KAFKA_BROKERS", "kafka:9092")
    monkeypatch.setenv(
        "POSTGRES_DATABASE_NAME", "student_alice-marketplace-ad-service-postgres"
    )
    configure_environment()
    import os

    assert os.environ["DATABASE_URL"] == "postgresql+asyncpg://user:pass@db/test"
    assert os.environ["KAFKA_BOOTSTRAP_SERVERS"] == "kafka:9092"
    assert os.environ["AUTH_SERVICE_URL"] == (
        "http://student-alice-marketplace-auth-service-web."
        "student-alice-marketplace-auth-service.svc:8000"
    )


def test_explicit_configuration_wins(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://explicit/db")
    monkeypatch.setenv("POSTGRES_CONNECTION_STRING", "postgres://platform/db")
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "explicit:9092")
    monkeypatch.setenv("KAFKA_BROKERS", "platform:9092")
    configure_environment()
    import os

    assert os.environ["DATABASE_URL"] == "postgresql+asyncpg://explicit/db"
    assert os.environ["KAFKA_BOOTSTRAP_SERVERS"] == "explicit:9092"
