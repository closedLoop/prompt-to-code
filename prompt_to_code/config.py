import os
from dataclasses import dataclass
from pathlib import Path

import dotenv

from prompt_to_code.logger import FileLoggerConfig, LoggerConfig, StreamLoggerConfig

dotenv.load_dotenv()


@dataclass
class PromptToCodeConfig:
    output_directory: Path = Path(os.environ.get("P2C_OUTPUT_DIRECTORY", "."))
    openai_api_key: str | None = os.environ.get("OPENAI_API_KEY", None)

    logging: LoggerConfig = LoggerConfig(
        stream=StreamLoggerConfig(
            level=int(os.environ.get("P2C_LOG_LEVEL", StreamLoggerConfig.level) or 10),
            format=os.environ.get("P2C_LOG_FORMAT", StreamLoggerConfig.format),
            enabled=bool(os.environ.get("P2C_LOG_ENABLED", StreamLoggerConfig.enabled)),
        ),
        file=FileLoggerConfig(
            level=int(
                os.environ.get("P2C_LOGFILE_LEVEL", FileLoggerConfig.level) or 20
            ),
            format=os.environ.get("P2C_LOGFILE_FORMAT", FileLoggerConfig.format),
            enabled=bool(
                os.environ.get("P2C_LOGFILE_ENABLED", FileLoggerConfig.enabled)
            ),
            maxBytes=int(
                os.environ.get("P2C_LOGFILE_MAX_BYTES", FileLoggerConfig.maxBytes)
            ),
            backupCount=int(
                os.environ.get("P2C_LOGFILE_BACKUP_COUNT", FileLoggerConfig.backupCount)
            ),
            filename=os.environ.get("P2C_LOGFILE_FILE_NAME", FileLoggerConfig.filename),
            log_directory=os.environ.get(
                "P2C_LOGFILE_DIRECTORY", FileLoggerConfig.log_directory
            ),
        ),
    )


if __name__ == "__main__":
    config = PromptToCodeConfig()
    print(config)
