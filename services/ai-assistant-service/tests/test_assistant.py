import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure service root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.pricing_engine import pricing_engine

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ai-assistant-service"
    assert data["status"] == "UP"
    assert data["language"] == "Python"
    print("[PASS] Health check passed:", data)

def test_config():
    response = client.get("/assistant/config")
    assert response.status_code == 200
    data = response.json()
    assert "openai_configured" in data
    assert "model" in data
    print("[PASS] Config check passed:", data)

def test_list_products():
    response = client.get("/assistant/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 6
    names = [p["name"] for p in products]
    assert "AI Mechanical Keyboard" in names
    assert "CloudOps Headset" in names
    print(f"[PASS] Product listing passed, total products: {len(products)}")

def test_pricing_engine():
    # 3x Keyboard ($79.99 each) = $239.97
    # 3 items qualifies for 5% bulk discount: $239.97 * 0.05 = $12.00
    # Promo DEVOPS10: 10% off raw subtotal = $24.00
    items = [
        {"product_id": 1, "name": "AI Mechanical Keyboard", "price": 79.99, "quantity": 3}
    ]
    calc = pricing_engine.calculate(items, promo_code="DEVOPS10")
    assert calc["total_items"] == 3
    assert calc["subtotal"] == 239.97
    assert len(calc["discounts"]) == 2  # Volume + Promo
    assert calc["subtotal_after_discount"] < calc["subtotal"]
    # Over $100 after discount -> Free shipping
    assert calc["shipping"] == 0.00
    print("[PASS] Pricing engine passed:", calc)

def test_pricing_endpoint():
    payload = {
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ],
        "promo_code": "DEVOPS10",
        "tax_rate": 0.08
    }
    response = client.post("/assistant/pricing/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 3
    assert "grand_total" in data
    print("[PASS] Pricing endpoint passed, grand total:", data["grand_total"])

def test_chat_product_info():
    payload = {
        "message": "Can you recommend a mechanical keyboard and tell me about it?"
    }
    response = client.post("/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 20
    print("[PASS] Chat product info passed. Reply snippet:", data["reply"][:120].replace('\n', ' '), "...")

def test_chat_pricing_quote():
    payload = {
        "message": "How much for 3 CloudOps Headsets with promo code DEVOPS10?"
    }
    response = client.post("/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 20
    print("[PASS] Chat pricing quote passed. Reply snippet:", data["reply"][:120].replace('\n', ' '), "...")

if __name__ == "__main__":
    test_health()
    test_config()
    test_list_products()
    test_pricing_engine()
    test_pricing_endpoint()
    test_chat_product_info()
    test_chat_pricing_quote()
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")
