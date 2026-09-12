import asyncio
from decimal import Decimal
from services.catalog.db import SessionLocal, init_db
from services.catalog.models import Product

PRODUCTS = [
    ("SKU-1001", "Enterprise Laptop", "Business laptop", Decimal("89999.00"), 100),
    ("SKU-1002", "Mechanical Keyboard", "Professional keyboard", Decimal("6999.00"), 250),
    ("SKU-1003", "4K Monitor", "27 inch 4K monitor", Decimal("32999.00"), 80),
    ("SKU-1004", "USB-C Dock", "Universal USB-C docking station", Decimal("9999.00"), 120),
]

async def main():
    await init_db()
    async with SessionLocal() as db:
        for sku, name, description, price, stock in PRODUCTS:
            db.add(Product(sku=sku, name=name, description=description, price=price, stock=stock))
        await db.commit()
    print("Catalog seed completed.")

if __name__ == "__main__":
    asyncio.run(main())
