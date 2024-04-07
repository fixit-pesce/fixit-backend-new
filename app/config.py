from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # JWT Config
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    # Database Config
    mongo_url: str
    mongo_db: str
    mongo_db_test: str

    # Admin Data
    admin_username: str
    admin_email: str
    admin_first_name: str
    admin_last_name: str
    admin_password: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()