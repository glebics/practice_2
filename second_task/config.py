from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str

    class Config:
        env_file = ".env"
        env_prefix = "DB_"
        case_sensitive = True

    @property
    def database_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            user=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            port=str(self.db_port),
            path=f"/{self.db_name}",
        )


settings = Settings()
