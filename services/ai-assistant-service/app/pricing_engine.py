from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP

PROMO_CODES = {
    "DEVOPS10": {"type": "percentage", "value": Decimal("0.10"), "desc": "10% DevOps Shack community discount"},
    "CLOUD20": {"type": "percentage", "value": Decimal("0.20"), "desc": "20% Cloud Native discount"},
    "WELCOME5": {"type": "flat", "value": Decimal("5.00"), "min_subtotal": Decimal("25.00"), "desc": "$5 off welcome coupon"},
    "SHACKFREE": {"type": "free_shipping", "desc": "Free standard shipping coupon"},
}

def round_cur(val: Decimal) -> float:
    return float(val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

class PricingEngine:
    @staticmethod
    def calculate(
        items: List[Dict[str, Any]],
        promo_code: Optional[str] = None,
        tax_rate: float = 0.08,
    ) -> Dict[str, Any]:
        """
        Calculate total price breakdown.
        Each item is expected to have:
          - 'product_id': int
          - 'name': str
          - 'price': float (unit price)
          - 'quantity': int
        """
        line_items = []
        raw_subtotal = Decimal("0.00")
        total_quantity = 0

        for it in items:
            qty = max(1, int(it.get("quantity", 1)))
            total_quantity += qty
            unit_price = Decimal(str(round(float(it.get("price", 0.0)), 2)))
            line_total = unit_price * qty
            raw_subtotal += line_total

            line_items.append({
                "product_id": it.get("product_id"),
                "name": it.get("name", f"Product #{it.get('product_id')}"),
                "unit_price": round_cur(unit_price),
                "quantity": qty,
                "line_total": round_cur(line_total),
            })

        applied_discounts = []
        total_discount = Decimal("0.00")

        # 1. Volume discount tiers
        volume_rate = Decimal("0.00")
        volume_label = ""
        if total_quantity >= 10:
            volume_rate = Decimal("0.15")
            volume_label = "15% Bulk Order Discount (10+ items)"
        elif total_quantity >= 5:
            volume_rate = Decimal("0.10")
            volume_label = "10% Team Order Discount (5-9 items)"
        elif total_quantity >= 3:
            volume_rate = Decimal("0.05")
            volume_label = "5% Multi-Pack Discount (3-4 items)"

        if volume_rate > 0:
            vol_disc = raw_subtotal * volume_rate
            total_discount += vol_disc
            applied_discounts.append({
                "name": volume_label,
                "amount": round_cur(vol_disc),
            })

        # 2. Promo code discount
        free_shipping_applied = False
        if promo_code:
            code = promo_code.strip().upper()
            promo = PROMO_CODES.get(code)
            if promo:
                if promo["type"] == "percentage":
                    p_disc = raw_subtotal * promo["value"]
                    total_discount += p_disc
                    applied_discounts.append({
                        "name": f"Promo '{code}' - {promo['desc']}",
                        "amount": round_cur(p_disc),
                    })
                elif promo["type"] == "flat":
                    min_sub = promo.get("min_subtotal", Decimal("0.00"))
                    if raw_subtotal >= min_sub:
                        p_disc = promo["value"]
                        total_discount += p_disc
                        applied_discounts.append({
                            "name": f"Promo '{code}' - {promo['desc']}",
                            "amount": round_cur(p_disc),
                        })
                elif promo["type"] == "free_shipping":
                    free_shipping_applied = True
                    applied_discounts.append({
                        "name": f"Promo '{code}' - {promo['desc']}",
                        "amount": 0.00,
                    })

        # Subtotal after discount cannot be negative
        subtotal_after_discount = max(Decimal("0.00"), raw_subtotal - total_discount)

        # 3. Shipping ($9.99 or free if subtotal >= $100 or free shipping coupon)
        if subtotal_after_discount >= Decimal("100.00") or free_shipping_applied or raw_subtotal == 0:
            shipping = Decimal("0.00")
            shipping_note = "Free Shipping (orders $100+ or promo)"
        else:
            shipping = Decimal("9.99")
            shipping_note = "Standard Flat-Rate Shipping ($9.99)"

        # 4. Tax
        tax = subtotal_after_discount * Decimal(str(tax_rate))

        # 5. Grand total
        grand_total = subtotal_after_discount + shipping + tax

        return {
            "items": line_items,
            "total_items": total_quantity,
            "subtotal": round_cur(raw_subtotal),
            "discount_amount": round_cur(total_discount),
            "discounts": applied_discounts,
            "subtotal_after_discount": round_cur(subtotal_after_discount),
            "shipping": round_cur(shipping),
            "shipping_note": shipping_note,
            "tax": round_cur(tax),
            "tax_rate_percent": round(tax_rate * 100, 1),
            "grand_total": round_cur(grand_total),
            "savings": round_cur(total_discount + (Decimal("9.99") if subtotal_after_discount >= 100 else Decimal("0.00"))),
        }

pricing_engine = PricingEngine()
