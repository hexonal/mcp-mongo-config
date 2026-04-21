from pathlib import Path

from mongodb_mcp.config import MongoDBConfig


def test_config_ignores_unrelated_env_keys(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "MONGODB_URI=mongodb://user:pass@example.com:27017/app",
                "MONGODB_ALLOW_DANGEROUS=true",
                "KIMI_API_KEY=should-be-ignored",
                "FEISHU_APP_ID=should-also-be-ignored",
            ]
        )
        + "\n"
    )

    config = MongoDBConfig(_env_file=env_file)

    assert config.mongodb_uri == "mongodb://user:pass@example.com:27017/app"
    assert config.mongodb_allow_dangerous is True


def test_config_builds_uri_from_fields(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "MONGODB_HOST=mongo-a,mongo-b",
                "MONGODB_PORT=3717",
                "MONGODB_DATABASE=ai_nexus_us",
                "MONGODB_USERNAME=reader",
                "MONGODB_PASSWORD=secret",
                "MONGODB_AUTH_DB=ai_nexus_us",
            ]
        )
        + "\n"
    )

    config = MongoDBConfig(_env_file=env_file)

    assert (
        config.connection_uri
        == "mongodb://reader:secret@mongo-a:3717,mongo-b:3717/ai_nexus_us"
        "?authSource=ai_nexus_us&replicaSet=rs0&readPreference=secondaryPreferred"
        "&retryWrites=true"
    )
