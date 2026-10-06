from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ParserConfig(BaseSettings):
    data_dir: Path = Path("data")
    file_glob: str = "*.json"   
    encoding: str = "utf-8-sig"
    fail_on_invalid: bool = True

    model_config = SettingsConfigDict(
        env_prefix="PARSER_",
        env_file=".env",
        extra="ignore",
    )


parser_settings = ParserConfig()