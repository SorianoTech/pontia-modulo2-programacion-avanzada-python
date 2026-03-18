from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Carga variables desde el entorno o desde un archivo .env si existe.
    """

    # Base de datos
    DATABASE_URL: str = "sqlite:///./todos.db"


    # Configuración de carga (prioriza variables de entorno, luego .env)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instancia global de configuración
settings = Settings()
