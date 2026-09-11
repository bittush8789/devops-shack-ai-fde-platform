# Architecture Summary

```text
                                  React UI :5173
                                        |
    +----------+----------+----------+----------+----------+----------+-----------------------+
    |          |          |          |          |          |          |                       |
  Auth      Catalog    Inventory   Orders    Payments   Notifications Analytics          AI Assistant
  Java       Go        Node.js     Python      C#          Ruby         PHP                 Python
 :8081      :8082      :8083      :8084      :8085       :8086        :8087                 :8088
    |          |          |          |          |           |           |                     |
 auth_db  catalog_db inventory_db order_db payment_db notification_db analytics_db    OpenAI + Catalog REST
```

The Order Service calls Catalog and Inventory.
The Payment Service calls Orders.
Orders and Payments call Notifications.
Analytics calls Catalog, Inventory, Orders and Payments.
The AI Assistant calls Catalog and Inventory, and queries the Chroma DB vector database (:8000) for RAG semantic search across internal product specs, architecture, and store policies.
