import asyncio
import os
import httpx

URLS = [
    os.getenv("GATEWAY_URL", "http://localhost:8000") + "/health",
    os.getenv("AUTH_URL", "http://localhost:8001") + "/health",
    os.getenv("CATALOG_URL", "http://localhost:8002") + "/health",
    os.getenv("ORDERS_URL", "http://localhost:8003") + "/health",
]

async def main():
    async with httpx.AsyncClient(timeout=5) as client:
        for url in URLS:
            response = await client.get(url)
            print(url, response.status_code, response.text)

if __name__ == "__main__":
    asyncio.run(main())
