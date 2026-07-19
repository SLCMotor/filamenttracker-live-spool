import uvicorn

from app.core.config import config


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        log_level=config.log_level,
    )


if __name__ == "__main__":
    main()
