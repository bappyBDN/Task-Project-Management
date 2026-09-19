from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Anwar Group Enterprise Task & Project Management System"
    database_url: str = "sqlite:///./anwar_task_manager.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
