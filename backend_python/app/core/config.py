from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017/personal_finance_advisor"
    JWT_SECRET: str = "your_jwt_secret_here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    SHOW_DEMO_RESET_LINK: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
