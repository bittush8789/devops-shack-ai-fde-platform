import logging
import time
from typing import Optional, List, Dict, Any
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback dataset matching the seeded products in catalog-service and inventory-service
SEED_PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "AI Mechanical Keyboard",
        "category": "Workspace",
        "description": "Low-profile mechanical keyboard designed for coding sessions. Features hot-swappable switches, RGB backlighting, and programmable macros.",
        "price": 79.99,
        "image": "⌨️",
        "active": True,
        "stock": 60,
    },
    {
        "id": 2,
        "name": "CloudOps Headset",
        "category": "Audio",
        "description": "Comfortable USB headset for standups and incident calls. Features active noise cancellation, boom mic, and padded earcups.",
        "price": 64.50,
        "image": "🎧",
        "active": True,
        "stock": 45,
    },
    {
        "id": 3,
        "name": "Kubernetes Desk Mat",
        "category": "Workspace",
        "description": "Large desk mat with Kubernetes command references, kubectl cheatsheets, and architecture diagrams. High-density rubber base.",
        "price": 29.00,
        "image": "☸️",
        "active": True,
        "stock": 85,
    },
    {
        "id": 4,
        "name": "DevSecOps Security Key",
        "category": "Security",
        "description": "Hardware security-key demo product for MFA workflows, FIDO2/U2F compliance, and secure cloud console authentication.",
        "price": 49.99,
        "image": "🔐",
        "active": True,
        "stock": 25,
    },
    {
        "id": 5,
        "name": "Observability Display",
        "category": "Hardware",
        "description": "Portable 1080p IPS display for metrics and Grafana dashboards. USB-C powered with ultra-slim bezel.",
        "price": 189.00,
        "image": "📊",
        "active": True,
        "stock": 8,
    },
    {
        "id": 6,
        "name": "SRE Incident Notebook",
        "category": "Learning",
        "description": "Structured notebook for runbooks, incidents, on-call notes, and postmortems. Waterproof pages with incident response templates.",
        "price": 18.75,
        "image": "📘",
        "active": True,
        "stock": 120,
    },
]

class CatalogClient:
    def __init__(self, catalog_url: str = settings.CATALOG_URL, inventory_url: str = settings.INVENTORY_URL):
        self.catalog_url = catalog_url
        self.inventory_url = inventory_url
        self._unreachable_until: float = 0.0

    async def get_all_products(self) -> List[Dict[str, Any]]:
        """Fetch all products from catalog-service, or fallback to SEED_PRODUCTS."""
        if time.time() < self._unreachable_until:
            return [dict(p) for p in SEED_PRODUCTS]

        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                res = await client.get(f"{self.catalog_url}/products")
                if res.status_code == 200:
                    items = res.json()
                    # Attempt to enrich with inventory stock
                    try:
                        inv_res = await client.get(f"{self.inventory_url}/inventory")
                        if inv_res.status_code == 200:
                            inv_map = {item.get("product_id"): item.get("available", 0) for item in inv_res.json()}
                            for it in items:
                                it["stock"] = inv_map.get(it["id"], "In Stock")
                    except Exception:
                        pass
                    return items
        except Exception as e:
            self._unreachable_until = time.time() + 60.0
            logger.warning(f"Catalog service unreachable at {self.catalog_url} ({e}); using fallback seed catalog")

        return [dict(p) for p in SEED_PRODUCTS]

    async def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Fetch product by ID."""
        if time.time() < self._unreachable_until:
            for p in SEED_PRODUCTS:
                if p["id"] == product_id:
                    return dict(p)
            return None

        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                res = await client.get(f"{self.catalog_url}/products/{product_id}")
                if res.status_code == 200:
                    data = res.json()
                    try:
                        inv_res = await client.get(f"{self.inventory_url}/inventory/{product_id}")
                        if inv_res.status_code == 200:
                            data["stock"] = inv_res.json().get("available", 0)
                    except Exception:
                        pass
                    return data
        except Exception:
            pass

        for p in SEED_PRODUCTS:
            if p["id"] == product_id:
                return dict(p)
        return None

    async def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Search products with query, category, and price filters."""
        all_products = await self.get_all_products()
        results = []

        q_lower = query.lower().strip() if query else ""
        c_lower = category.lower().strip() if category else ""

        for p in all_products:
            if not p.get("active", True):
                continue

            name = p.get("name", "").lower()
            cat = p.get("category", "").lower()
            desc = p.get("description", "").lower()
            price = float(p.get("price", 0))

            if q_lower and not (q_lower in name or q_lower in cat or q_lower in desc):
                continue
            if c_lower and c_lower not in cat:
                continue
            if max_price is not None and price > max_price:
                continue

            results.append(p)

        return results

    async def compare_products(self, product_ids: List[int]) -> List[Dict[str, Any]]:
        """Retrieve comparison details for multiple products."""
        items = []
        for pid in product_ids:
            prod = await self.get_product_by_id(pid)
            if prod:
                items.append(prod)
        return items

catalog_client = CatalogClient()
