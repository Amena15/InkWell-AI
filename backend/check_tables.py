import asyncio
from sqlalchemy import inspect
from app.database import engine, Base

async def check_tables():
    async with engine.connect() as conn:
        # Use run_sync to run synchronous code in an async context
        def sync_inspect(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()
            
        tables = await conn.run_sync(sync_inspect)
        print("Tables in the database:")
        for table in tables:
            print(f"- {table}")

if __name__ == "__main__":
    asyncio.run(check_tables())
