"""EMBEDHUNT AI — Entry Point"""
import uvicorn
from app.config.settings import settings
if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=not settings.is_production, workers=1 if not settings.is_production else settings.WORKERS)
