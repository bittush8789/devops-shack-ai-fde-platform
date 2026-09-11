from typing import List, Dict, Any

# Structured knowledge chunks internal to the Polyglot Commerce app and products
INTERNAL_KNOWLEDGE: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # 1. Product Specifications & Deep Technical Information
    # -------------------------------------------------------------
    {
        "id": "prod-1-keyboard-specs",
        "title": "AI Mechanical Keyboard - Technical Specifications & Features",
        "category": "Products",
        "tags": ["keyboard", "hardware", "workspace", "ergonomics", "coding"],
        "content": (
            "AI Mechanical Keyboard (Price: $79.99, Category: Workspace). "
            "Engineered specifically for software engineers and coding sessions. "
            "Key switches: Hot-swappable low-profile Gateron mechanical switches (factory pre-lubed for tactile, quiet keystrokes). "
            "Keycaps: Premium PBT dye-sublimated keycaps resistant to shine and oil. "
            "Layout: Compact 75% ANSI layout preserving arrow keys and dedicated function row. "
            "Connectivity: Tri-mode connectivity supporting Bluetooth 5.2 (up to 3 paired devices), 2.4GHz ultra-low latency wireless dongle, and USB-C wired mode. "
            "Battery life: 4,000 mAh rechargeable battery offering up to 200 hours of continuous typing with backlighting off, or 40 hours with RGB active. "
            "Firmware: Fully programmable with QMK and VIA open-source firmware; includes a dedicated hardware macro key programmable for AI coding assistants (Copilot, Gemini, ChatGPT)."
        ),
    },
    {
        "id": "prod-2-headset-specs",
        "title": "CloudOps Headset - Technical Specifications & Audio Quality",
        "category": "Products",
        "tags": ["headset", "audio", "incident", "standup", "anc"],
        "content": (
            "CloudOps Headset (Price: $64.50, Category: Audio). "
            "Designed for engineering incident triage calls, daily standups, and uninterrupted deep work. "
            "Drivers: 40mm custom neodymium audio drivers tuned for vocal clarity and crisp speech separation. "
            "Noise Cancellation: Hybrid Active Noise Cancellation (ANC) attenuates ambient office and keyboard noise by up to 35 dB. "
            "Microphone: Flexible boom microphone equipped with dual-mic AI environmental noise suppression (ENC); features flip-to-mute with an integrated red LED status ring. "
            "Connectivity: Dual USB-A and USB-C plug-and-play adapter plus a detachable 3.5mm analog cable. No driver installation required on Linux, macOS, or Windows. "
            "Ergonomics: Memory foam protein leather earcups with an adjustable steel-reinforced headband; ultra-lightweight at only 210 grams for all-day comfort during on-call shifts."
        ),
    },
    {
        "id": "prod-3-deskmat-specs",
        "title": "Kubernetes Desk Mat - Dimensions & Reference Guide",
        "category": "Products",
        "tags": ["desk mat", "kubernetes", "k8s", "cheatsheet", "workspace"],
        "content": (
            "Kubernetes Desk Mat (Price: $29.00, Category: Workspace). "
            "An oversized precision desk mat featuring comprehensive Kubernetes architectural diagrams and kubectl command cheat sheets. "
            "Dimensions: Extra-large format measuring 900mm x 400mm x 4mm (35.4 x 15.7 inches), easily accommodating keyboard, mouse, and phone. "
            "Cheatsheet contents printed on surface: Pod lifecycle commands, Deployments, ReplicaSets, StatefulSets, DaemonSets, Services (ClusterIP, NodePort, LoadBalancer), "
            "Ingress, Namespaces, ConfigMaps, Secrets, RBAC, rollout history/undo commands, kubectl exec, kubectl port-forward, and JSONPath output formatting. "
            "Materials: Ultra-smooth micro-woven cloth surface optimized for optical gaming mouse tracking; 4mm dense natural rubber anti-slip base; anti-fray precision stitched edges. "
            "Maintenance: Hydrophobic spill-resistant coating; easily cleaned with a damp microfiber cloth."
        ),
    },
    {
        "id": "prod-4-securitykey-specs",
        "title": "DevSecOps Security Key - Hardware Security & MFA Protocols",
        "category": "Products",
        "tags": ["security", "mfa", "fido2", "webauthn", "devsecops"],
        "content": (
            "DevSecOps Security Key (Price: $49.99, Category: Security). "
            "Hardware authentication token designed for zero-trust engineering environments and cloud console MFA. "
            "Security standards: FIDO2 / WebAuthn certified, FIDO U2F, OATH-TOTP, OATH-HOTP, and OpenPGP smartcard compatible (RSA 4096 / ECC). "
            "Physical interface: Dual interface with USB-C connector and contactless NFC for tap-to-authenticate on Android and iOS devices. "
            "Form factor: Ultra-compact keyhole design constructed with tamper-evident, glass-fiber reinforced composite; rated IP68 water and dust resistant. "
            "Compatibility: Works natively across AWS Management Console, Google Cloud Platform, Microsoft Azure, GitHub, GitLab, Okta, 1Password, and Linux PAM ssh-keygen with ecdsa-sk keys."
        ),
    },
    {
        "id": "prod-5-display-specs",
        "title": "Observability Display - Portable Dashboard Monitor Specs",
        "category": "Products",
        "tags": ["display", "monitor", "grafana", "observability", "hardware"],
        "content": (
            "Observability Display (Price: $189.00, Category: Hardware). "
            "Ultra-portable secondary monitor dedicated to real-time Grafana dashboards, Prometheus metrics, server logs, and APM tracing. "
            "Screen specifications: 15.6-inch Full HD (1920x1080) IPS anti-glare panel, 100% sRGB color gamut, 300 nits brightness, 178-degree wide viewing angles, 60Hz refresh rate. "
            "Connectivity: Dual full-featured USB Type-C ports (video transmission and USB-PD passthrough power over a single cable) plus Mini-HDMI port. "
            "Audio & Extras: Integrated dual stereo speakers (2W x 2), 3.5mm headphone audio output jack, low blue light eye-care filter. "
            "Portability: Ultra-slim 5mm profile weighing only 680 grams (1.5 lbs); includes magnetic protective folding smart cover that doubles as a multi-angle stand supporting landscape and portrait orientation."
        ),
    },
    {
        "id": "prod-6-notebook-specs",
        "title": "SRE Incident Notebook - Runbooks, Postmortems & Field Templates",
        "category": "Products",
        "tags": ["notebook", "sre", "incidents", "runbook", "learning"],
        "content": (
            "SRE Incident Notebook (Price: $18.75, Category: Learning). "
            "A structured operational field notebook created for Site Reliability Engineers, DevOps teams, and on-call responders. "
            "Format & Binding: Standard A5 size (5.8 x 8.3 inches), 160 numbered pages, durable matte hardcover with dual ribbon page markers and expandable rear pocket. "
            "Paper technology: Crafted with 120gsm synthetic stone paper that is 100% waterproof, tear-resistant, and grease-proof; impervious to coffee spills during 3 AM incident responses. "
            "Template sections: 40 incident triage logs (severity categorization P1-P4, timestamped timeline, hypotheses, mitigation steps), 15 Blameless Postmortem worksheets "
            "(Root Cause Analysis 5-Whys, contributing factors, preventative action items), and 30 dot-grid architecture sketching pages."
        ),
    },

    # -------------------------------------------------------------
    # 2. Platform Architecture, Microservices & Ports
    # -------------------------------------------------------------
    {
        "id": "arch-polyglot-overview",
        "title": "DevOps Shack Polyglot Architecture & Microservices Overview",
        "category": "Architecture",
        "tags": ["architecture", "microservices", "languages", "ports", "polyglot"],
        "content": (
            "The Polyglot Commerce platform consists of independent microservices built in 7 programming languages, each with isolated data ownership: "
            "1. Auth Service: Java 21 + Spring Boot (Port 8081, DB: auth_db). Handles user signup, login, JWT token issuance, and validation. "
            "2. Catalog Service: Go (Port 8082, DB: catalog_db). Manages product inventory items, metadata, categories, prices, and CRUD endpoints (/products). "
            "3. Inventory Service: Node.js + Express (Port 8083, DB: inventory_db). Tracks physical stock, reserved quantities, and reorder levels. "
            "4. Order Service: Python + FastAPI (Port 8084, DB: order_db). Orchestrates order placement, queries Catalog for pricing, and calls Inventory to reserve items. "
            "5. Payment Service: C# / .NET 8 (Port 8085, DB: payment_db). Processes simulated card payments and records transactions. "
            "6. Notification Service: Ruby + Sinatra (Port 8086, DB: notification_db). Logs and delivers email/alerts upon order events. "
            "7. Analytics Service: PHP (Port 8087, DB: analytics_db). REST aggregation for captured revenue, order counts, and low stock metrics. "
            "8. Chroma DB: Vector database (Port 8000). Houses embeddings for Retrieval-Augmented Generation (RAG). "
            "9. AI Assistant Service: Python + FastAPI (Port 8088). Integrates OpenAI models and Chroma DB RAG for product and pricing assistance. "
            "10. Frontend: React + Vite + Nginx Reverse Proxy (Port 5173)."
        ),
    },
    {
        "id": "arch-service-communication",
        "title": "Microservices Communication Flow & Inter-Service REST Calls",
        "category": "Architecture",
        "tags": ["networking", "rest", "flow", "orders", "inventory"],
        "content": (
            "Inter-service communication flow in DevOps Shack Polyglot Commerce: "
            "1. Order Placement Flow: When a client posts an order to the Order Service (Python :8084), the Order Service calls Catalog Service (Go :8082) "
            "to verify active products and unit prices, then calls Inventory Service (Node.js :8083) to reserve stock. "
            "2. Payment Flow: When payment is initiated on Payment Service (C# :8085), it verifies the order status with Order Service and triggers Notifications (Ruby :8086). "
            "3. Notification Flow: Both Order Service and Payment Service send event webhooks to Notification Service (Ruby :8086). "
            "4. Analytics Flow: The Analytics Service (PHP :8087) regularly polls Catalog, Inventory, Orders, and Payments APIs to aggregate business intelligence. "
            "5. AI Assistant Flow: The AI Assistant Service (Python :8088) queries Catalog Service for live prices and Chroma DB (Port 8000) for RAG semantic search."
        ),
    },

    # -------------------------------------------------------------
    # 3. Store Policies, Discounts & Pricing Rules
    # -------------------------------------------------------------
    {
        "id": "policy-discounts-promos",
        "title": "Promotional Discount Codes & Bulk Pricing Rules",
        "category": "Pricing",
        "tags": ["discounts", "coupons", "promo", "pricing", "bulk"],
        "content": (
            "DevOps Shack Polyglot Commerce promotional discount codes: "
            "1. 'DEVOPS10': 10% discount across the entire cart for DevOps community members. "
            "2. 'CLOUD20': 20% discount on cloud and security gear. "
            "3. 'WELCOME5': $5.00 flat discount on orders over $25.00. "
            "4. 'SHACKFREE': Free standard shipping on any order regardless of subtotal. "
            "Tiered Bulk Quantity Discounts (automatically calculated and applied): "
            "- 3 to 4 items: 5% bulk discount. "
            "- 5 to 9 items: 10% team discount. "
            "- 10+ items: 15% enterprise volume discount. "
            "Shipping Policy: Orders with subtotal after discounts of $100.00 or more receive Free Standard Shipping. Orders under $100 have flat $9.99 shipping. "
            "Estimated Tax: Standard 8% sales tax applied to the discounted subtotal."
        ),
    },
    {
        "id": "policy-returns-warranty",
        "title": "Shipping, Returns, Warranty & Refund Policies",
        "category": "Policies",
        "tags": ["returns", "shipping", "warranty", "refunds"],
        "content": (
            "Store policies for DevOps Shack Polyglot Commerce: "
            "Shipping: Orders are dispatched within 24 hours from local fulfillment centers. Standard delivery takes 2-4 business days. Free shipping on orders over $100. "
            "Returns & Guarantee: We offer a 30-day money-back guarantee. If you are not completely satisfied with your developer gear, return it in original packaging within 30 days. "
            "Warranty: Hardware products (AI Mechanical Keyboard, Observability Display, CloudOps Headset, DevSecOps Key) include a 1-year manufacturer replacement warranty covering defects. "
            "Cancellations: Orders can be cancelled instantly before they transition to 'PROCESSING' or 'SHIPPED' status. When cancelled, inventory reservations are automatically released."
        ),
    },
    {
        "id": "workflow-inventory-reservation",
        "title": "Inventory Reservation & Stock Locking Lifecycle",
        "category": "Workflows",
        "tags": ["inventory", "reservation", "concurrency", "orders"],
        "content": (
            "Inventory reservation lifecycle: When a customer submits an order, the Order Service requests an atomic stock reservation from the Inventory Service. "
            "The Inventory Service increments the 'reserved' column in PostgreSQL table 'inventory' without immediately decrementing 'quantity'. "
            "This ensures that stock is held exclusively for that customer. If payment succeeds, the reservation is permanently committed. "
            "If the order is cancelled or times out, the Inventory Service releases the reservation, returning the items to available stock."
        ),
    },
]
