# libs
from pydantic import BaseModel
from pydantic import SecretStr

from typing import Optional


class Settings(BaseModel):
    
    APP_NAME:   str  = "resume-teddy-app"
    API_V1_STR: str  = "/api/v1"
    DEBUG:      bool = True

    # Db Configurations
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_DB_NAME: str = "my_app_db"

    MONGODB_USER: Optional[str] = None
    MONGODB_PASSWORD: Optional[SecretStr] = None
    MONGODB_AUTH_SOURCE: str = "admin"

    class config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def mongodb_uri(self):
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            pwd = self.MONGODB_PASSWORD.get_secret_value()

            return f"mongodb+srv://{self.MONGODB_USER}:{pwd}@{self.MONGODB_DB_NAME}.fwxmw39.mongodb.net/?appName={self.MONGODB_DB_NAME}"
        
        return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}"