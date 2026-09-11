import json
import time
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

from app.config import settings
from app.catalog_client import catalog_client
from app.pricing_engine import pricing_engine, PROMO_CODES
from app.rag.retriever import rag_retriever
from app.guardrails.manager import guardrail_manager

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the DevOps Shack Polyglot Store AI Assistant, an expert consultant on developer hardware, accessories, tooling, internal microservices architecture, and pricing.

Your responsibilities:
1. Provide accurate product information, features, deep hardware specs, compatibility, categories, and inventory availability.
2. Help users with pricing inquiries, volume discounts, promo codes, tax, and itemized cost calculations.
3. Help users compare products to decide what best fits their engineering and workspace workflow.
4. Answer questions about the internal platform architecture, microservices (Java, Go, Node, Python, C#, Ruby, PHP), databases, and store policies using your internal knowledge base (RAG via Chroma DB).

Guidelines:
- Always use the provided tools to query real product catalog data, search internal knowledge in Chroma DB, and calculate exact prices.
- When answering questions about detailed hardware specs (e.g. switch types, ANC specs, kubectl commands, FIDO2 compatibility) or system architecture, search internal knowledge in Chroma DB.
- Available promo codes:
  * 'DEVOPS10': 10% discount for DevOps Shack community members
  * 'CLOUD20': 20% discount on cloud tools
  * 'WELCOME5': $5 flat discount on orders over $25
  * 'SHACKFREE': Free shipping
- Volume discount tiers:
  * 3-4 items: 5% off
  * 5-9 items: 10% off
  * 10+ items: 15% off
- Orders over $100 receive free shipping automatically.
- Standard shipping is $9.99.
- Maintain a helpful, friendly, and professional developer-first tone. Format responses with clean Markdown bullet points and bold highlights.
"""

# Tool schemas for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search products in the catalog by keyword, category, or maximum price.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword to search in product name or description (e.g. 'keyboard', 'headset', 'notebook')",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category: 'Workspace', 'Audio', 'Security', 'Hardware', 'Learning'",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum budget / price filter",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Retrieve comprehensive details, pricing, and stock for a specific product by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "The unique product ID (e.g., 1, 2, 3)",
                    },
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_pricing",
            "description": "Calculate exact pricing breakdown for items including volume discounts, promo code discounts, shipping, and tax.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "description": "List of products and quantities to quote",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "integer", "description": "Product ID"},
                                "quantity": {"type": "integer", "description": "Quantity needed"},
                            },
                            "required": ["product_id", "quantity"],
                        },
                    },
                    "promo_code": {
                        "type": "string",
                        "description": "Optional coupon/promo code (e.g. 'DEVOPS10', 'CLOUD20', 'WELCOME5', 'SHACKFREE')",
                    },
                },
                "required": ["items"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_products",
            "description": "Compare 2 or more products side by side regarding price, features, and category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of product IDs to compare",
                    },
                },
                "required": ["product_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_internal_knowledge",
            "description": "Query Chroma DB vector database for internal product specs, hardware features, architecture, microservices, store policies, discounts, and workflows.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Semantic query describing the needed internal information",
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter: 'Products', 'Architecture', 'Pricing', 'Policies', 'Workflows'",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

class AIAssistant:
    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self._circuit_broken_until: float = 0.0
        if settings.is_openai_configured():
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute local tool functions called by OpenAI."""
        try:
            if name == "search_internal_knowledge":
                query = args.get("query", "")
                cat = args.get("category")
                return rag_retriever.query(query, n_results=3, category=cat)

            elif name == "search_products":
                return await catalog_client.search_products(
                    query=args.get("query"),
                    category=args.get("category"),
                    max_price=args.get("max_price"),
                )

            elif name == "get_product_details":
                pid = args.get("product_id")
                prod = await catalog_client.get_product_by_id(pid)
                return prod or {"error": f"Product with ID {pid} not found"}

            elif name == "calculate_pricing":
                raw_items = args.get("items", [])
                promo_code = args.get("promo_code")

                enriched_items = []
                for it in raw_items:
                    pid = it.get("product_id")
                    qty = it.get("quantity", 1)
                    p = await catalog_client.get_product_by_id(pid)
                    if p:
                        enriched_items.append({
                            "product_id": p["id"],
                            "name": p["name"],
                            "price": p["price"],
                            "quantity": qty,
                        })
                    else:
                        enriched_items.append({
                            "product_id": pid,
                            "name": f"Product #{pid}",
                            "price": 0.0,
                            "quantity": qty,
                        })

                return pricing_engine.calculate(enriched_items, promo_code=promo_code)

            elif name == "compare_products":
                pids = args.get("product_ids", [])
                return await catalog_client.compare_products(pids)

            return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            logger.exception(f"Error executing tool {name}")
            return {"error": str(e)}

    async def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Process user message through guardrails and return assistant answer."""
        # 1. Pre-flight Guardrail Check
        guard_res = guardrail_manager.check_input(message)
        if not guard_res.allowed:
            return {
                "reply": guard_res.refusal_reply or "Request blocked by safety policy.",
                "tools_called": [],
                "mode": "guardrail_blocked",
                "model": settings.OPENAI_MODEL if settings.is_openai_configured() else "local-guardrail",
                "guardrails": {
                    "passed": False,
                    "blocked": True,
                    "risk_score": guard_res.risk_score,
                    "violations": guard_res.violations,
                    "checks": guard_res.checks,
                },
            }

        clean_message = guard_res.sanitized_text

        is_circuit_broken = time.time() < self._circuit_broken_until
        if not settings.is_openai_configured() or is_circuit_broken:
            res = await self._fallback_assistant(
                clean_message,
                history,
                notice="Operating in local catalog & pricing mode." if is_circuit_broken else "Note: OPENAI_API_KEY is not set in .env.openai. Operating in simulated catalog & pricing mode.",
            )
            res["guardrails"] = {
                "passed": True,
                "flagged": guard_res.flagged,
                "risk_score": guard_res.risk_score,
                "violations": guard_res.violations,
                "checks": guard_res.checks,
            }
            return res

        # Reinitialize client if needed
        if not self.client:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Pre-fetch relevant RAG internal knowledge from Chroma DB
        rag_context = rag_retriever.get_formatted_context(clean_message, n_results=2)
        system_content = SYSTEM_PROMPT
        if rag_context:
            system_content += f"\n\n{rag_context}\n\nUse this retrieved internal knowledge from Chroma DB to answer internal product and architecture questions accurately."

        messages = [{"role": "system", "content": system_content}]

        # Append conversation history
        if history:
            for h in history[-8:]:  # keep last 8 messages for context
                role = h.get("role", "user")
                if role in ("user", "assistant"):
                    messages.append({"role": role, "content": h.get("content", "")})

        messages.append({"role": "user", "content": clean_message})

        try:
            # Multi-turn tool execution loop (up to 4 steps)
            tools_called_log = []
            for _ in range(4):
                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                )

                choice = response.choices[0]
                res_msg = choice.message

                # If no tool calls, this is the final answer
                if not res_msg.tool_calls:
                    raw_reply = res_msg.content or "Here is the requested information."
                    has_leak, clean_reply, leak_violations = guardrail_manager.check_output(raw_reply)
                    return {
                        "reply": clean_reply,
                        "tools_called": tools_called_log,
                        "mode": "openai",
                        "model": settings.OPENAI_MODEL,
                        "guardrails": {
                            "passed": True,
                            "flagged": guard_res.flagged or has_leak,
                            "risk_score": guard_res.risk_score,
                            "violations": guard_res.violations + leak_violations,
                            "checks": guard_res.checks,
                        },
                    }

                # Otherwise, execute each tool call
                messages.append(res_msg)

                for tc in res_msg.tool_calls:
                    fn_name = tc.function.name
                    try:
                        fn_args = json.loads(tc.function.arguments)
                    except Exception:
                        fn_args = {}

                    tool_result = await self.execute_tool(fn_name, fn_args)
                    tools_called_log.append({"tool": fn_name, "args": fn_args})

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": fn_name,
                        "content": json.dumps(tool_result),
                    })

            # If loop finished without break, get final completion
            final_res = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
            )
            raw_reply = final_res.choices[0].message.content or "Here is the requested information."
            has_leak, clean_reply, leak_violations = guardrail_manager.check_output(raw_reply)
            return {
                "reply": clean_reply,
                "tools_called": tools_called_log,
                "mode": "openai",
                "model": settings.OPENAI_MODEL,
                "guardrails": {
                    "passed": True,
                    "flagged": guard_res.flagged or has_leak,
                    "risk_score": guard_res.risk_score,
                    "violations": guard_res.violations + leak_violations,
                    "checks": guard_res.checks,
                },
            }

        except Exception as e:
            err_str = str(e).lower()
            if "insufficient_quota" in err_str or "credit_balance_exhausted" in err_str or "invalid_api_key" in err_str:
                logger.warning("OpenAI quota exhausted / invalid key. Activating 300s circuit breaker.")
                self._circuit_broken_until = time.time() + 300.0

            logger.warning(f"OpenAI API call failed ({e}); falling back to local deterministic assistant")
            res = await self._fallback_assistant(
                clean_message,
                history,
                notice=f"OpenAI API request failed ({type(e).__name__}: {str(e)}). Switched to local catalog & pricing mode.",
            )
            res["guardrails"] = {
                "passed": True,
                "flagged": guard_res.flagged,
                "risk_score": guard_res.risk_score,
                "violations": guard_res.violations,
                "checks": guard_res.checks,
            }
            return res

    async def _fallback_assistant(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        notice: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Smart deterministic fallback when OpenAI API key is unconfigured or unavailable.
        Handles product inquiries, pricing lookups, and discount calculations directly.
        """
        text = message.lower()
        all_prods = await catalog_client.get_all_products()
        tools_called = []

        is_quote = any(w in text for w in ["calculate", "quote", "how much", "total for", "price for", "price of", "how much are", "how much is", "how much would"])

        matched_prod = None
        for p in all_prods:
            if p["name"].lower() in text or any(word in text for word in p["name"].lower().split() if len(word) > 3):
                matched_prod = p
                break

        # 1. Check for specific product quote / price calculation requests
        if is_quote and matched_prod:
            import re
            qty_match = re.search(r'\b(\d+)\b', text)
            qty = int(qty_match.group(1)) if qty_match else 1

            # Check promo code
            promo = None
            for code in PROMO_CODES:
                if code.lower() in text:
                    promo = code
                    break

            calc = pricing_engine.calculate(
                [{"product_id": matched_prod["id"], "name": matched_prod["name"], "price": matched_prod["price"], "quantity": qty}],
                promo_code=promo,
            )
            tools_called.append({"tool": "calculate_pricing", "args": {"product_id": matched_prod["id"], "qty": qty, "promo": promo}})

            reply_lines = [
                f"### 🧾 Price Estimate for {qty}x {matched_prod['name']}",
                f"- **Unit Price**: ${matched_prod['price']:.2f}",
                f"- **Subtotal ({qty} units)**: ${calc['subtotal']:.2f}",
            ]
            if calc['discounts']:
                for d in calc['discounts']:
                    reply_lines.append(f"- **Discount ({d['name']})**: -${d['amount']:.2f}")
                reply_lines.append(f"- **Subtotal After Discounts**: ${calc['subtotal_after_discount']:.2f}")

            reply_lines.append(f"- **Shipping**: ${calc['shipping']:.2f} ({calc['shipping_note']})")
            reply_lines.append(f"- **Estimated Tax ({calc['tax_rate_percent']}%)**: ${calc['tax']:.2f}")
            reply_lines.append(f"- **Grand Total**: **${calc['grand_total']:.2f}**")
            if calc['savings'] > 0:
                reply_lines.append(f"- 🎉 **Total Savings**: **${calc['savings']:.2f}**")

        # 2. Check for general pricing / discount code questions
        elif any(w in text for w in ["promo", "discount", "coupon", "code", "offer"]):
            reply_lines = [
                "### 🏷️ DevOps Shack Discount & Pricing Guide",
                "",
                "Here are our active discount programs and promotional codes:",
                "- **`DEVOPS10`**: **10% off** your entire order (DevOps community perk).",
                "- **`CLOUD20`**: **20% off** for Cloud Native developers.",
                "- **`WELCOME5`**: **$5.00 off** on orders over $25.00.",
                "- **`SHACKFREE`**: **Free standard shipping** (regularly $9.99).",
                "",
                "**Bulk Quantity Discounts** (automatically applied):",
                "- **3 to 4 items**: 5% off subtotal",
                "- **5 to 9 items**: 10% off subtotal",
                "- **10+ items**: 15% off subtotal",
                "- Orders over **$100.00** receive **Free Shipping** automatically!",
                "",
                "Let me know which products you are considering and I can prepare an exact quote for you!",
            ]
            tools_called.append({"tool": "get_promotions", "args": {}})

        # 3. Check for specific product lookup, deep specs, or internal RAG knowledge
        else:
            # Check Chroma DB vector search for internal knowledge
            rag_hits = rag_retriever.query(message, n_results=2)
            keywords = ["switch", "battery", "anc", "noise", "kubectl", "cheat", "fido", "mfa", "spec", "monitor", "display", "notebook", "runbook", "architecture", "microservice", "java", "go", "node", "python", "php", "ruby", "c#", "warranty", "return", "refund", "reserve", "how does", "what is", "dimensions", "specs"]
            is_internal_query = any(k in text for k in keywords)

            if rag_hits and (is_internal_query or rag_hits[0].get("distance", 2.0) < 0.85):
                reply_lines = ["### 📚 Internal Knowledge (Retrieved from Chroma DB)", ""]
                for h in rag_hits:
                    reply_lines.append(f"#### 🔍 {h['title']} *(`{h['category']}`)*")
                    reply_lines.append(f"{h['content']}")
                    reply_lines.append("")
                tools_called.append({"tool": "search_internal_knowledge", "args": {"hits": len(rag_hits), "top_title": rag_hits[0]["title"]}})
            else:
                matches = []
                for p in all_prods:
                    if any(k in text for k in [p["name"].lower(), p["category"].lower()]) or any(w in p["description"].lower() for w in text.split() if len(w) > 3):
                        matches.append(p)

                if matches:
                    reply_lines = [
                        "### 📦 Product Information & Pricing",
                        "",
                    ]
                    for p in matches[:4]:
                        reply_lines.append(f"#### {p.get('image', '📦')} {p['name']} — **${p['price']:.2f}**")
                        reply_lines.append(f"- **Category**: `{p['category']}`")
                        reply_lines.append(f"- **Description**: {p['description']}")
                        reply_lines.append(f"- **Availability**: {p.get('stock', 'In Stock')} units")
                        reply_lines.append("")
                    tools_called.append({"tool": "search_products", "args": {"matched_count": len(matches)}})
                else:
                    reply_lines = [
                        "### 👋 Welcome to the DevOps Shack AI Assistant!",
                        "",
                        "I can help you with product specifications, recommendations, and pricing breakdowns.",
                        "",
                        "**Our Products & Current Prices:**",
                    ]
                    for p in all_prods:
                        reply_lines.append(f"- {p.get('image', '📦')} **{p['name']}** (`{p['category']}`): **${p['price']:.2f}** — {p['description']}")

                    reply_lines.extend([
                        "",
                        "💡 *Try asking:*",
                        "- *'What hardware do you recommend for monitoring metrics?'*",
                        "- *'How much would 5 Mechanical Keyboards cost with discount code DEVOPS10?'*",
                        "- *'Compare the keyboard and desk mat'*",
                    ])

        if notice:
            reply_lines.append(f"\n> ℹ️ *{notice}*")

        raw_reply = "\n".join(reply_lines)
        has_leak, clean_reply, leak_violations = guardrail_manager.check_output(raw_reply)

        return {
            "reply": clean_reply,
            "tools_called": tools_called,
            "mode": "fallback_simulated",
            "model": "local-rules-engine",
            "guardrails": {
                "passed": True,
                "flagged": has_leak,
                "risk_score": 0.0,
                "violations": leak_violations,
                "checks": [],
            },
        }

assistant = AIAssistant()
