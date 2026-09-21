from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # `extra="ignore"` -> unknown keys in .env no longer crash the app on startup.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Anwar Group Enterprise Task & Project Management System"
    database_url: str = "sqlite:///./anwar_task_manager.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    frontend_url: str = "http://localhost:5173"

    # ---------------------------------------------------------------- Email (Gmail SMTP)
    # Set these in a .env file — never hardcode credentials in source.
    #   GMAIL_USER=youraddress@gmail.com
    #   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx      <- 16-char Google App Password (spaces are fine)
    #   MAIL_ENABLED=true
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465              # 465 = SSL, 587 = STARTTLS
    smtp_timeout_seconds: int = 30
    gmail_user: str = ""
    gmail_app_password: str = ""
    mail_enabled: bool = True

    # TEST MODE. When set, the app will ONLY ever send mail to these addresses; any other
    # recipient is silently dropped (and logged). Comma separated. Leave empty in production.
    #   MAIL_ALLOWED_RECIPIENTS=bappynath2001@gmail.com,bappydebath2001@gmail.com
    mail_allowed_recipients: str = ""

    # How often the background job re-scans tasks/backlog for emails.
    email_scan_interval_minutes: int = 60
    # A task due within this many days also gets a "due soon" reminder.
    task_due_lookahead_days: int = 3
    # A backlog item open this many days without conversion triggers a reminder.
    backlog_stale_days: int = 7
    # Only tasks completed within this many days get a "completed" email (avoids a flood of
    # old completed tasks the first time the scan runs on an existing database).
    completion_email_lookback_days: int = 7

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def mail_allowed_list(self) -> list[str]:
        return [a.strip().lower() for a in self.mail_allowed_recipients.split(",") if a.strip()]


settings = Settings()