"""EMBEDHUNT AI — DB Health Check"""
async def check_db_connection() -> bool:
    from sqlalchemy import text
    from app.database.session import AsyncSessionLocal
    try:
        async with AsyncSessionLocal() as s:
            await s.execute(text("SELECT 1"))
        return True
    except: return False
