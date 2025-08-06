from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_title: str = "SW Management API"

    sql_root_url: str
    sql_admin_url: str
    sql_manager_url: str
    sql_supervisor_url: str
    db_echo: bool = True

    allowed_origins: list = ["*"]
    allowed_credentials: bool = True
    allowed_methods: list = ["*"]
    allowed_headers: list = ["*"]

    jwt_secret: str
    jwt_algorithm: str = "HS256"


settings = Settings()
