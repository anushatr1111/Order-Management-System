# 📦 Order Management System

A production-ready **async REST API** built with **FastAPI**, following clean architecture principles.  
Supports full CRUD operations on orders with status lifecycle management, query filtering, structured logging, and CORS support.

---

## 🚀 Features

- ⚡ Async endpoints using FastAPI
- ✅ Pydantic v2 validation with detailed error messages
- 🏗️ Clean architecture — routes → services → models → database
- 🔁 Full CRUD: Create, Read, Update (status), Delete
- 🔍 Query filtering by order status (`?status=delivered`)
- 💉 Dependency injection for DB and service layers
- 🌐 CORS middleware (configurable)
- 📋 Structured logging across all layers
- 🧪 Swap-ready DB layer (in-memory dict → PostgreSQL / MongoDB with zero route changes)

---

## 🗂️ Project Structure

```
order-service/
├── main.py                  # App factory, CORS middleware, router registration
├── requirements.txt
├── database/
│   ├── __init__.py
│   └── in_memory_db.py      # In-memory store + FastAPI get_db() dependency
├── models/
│   ├── __init__.py
│   └── order_model.py       # Pydantic schemas: OrderCreate, OrderUpdate, OrderDB
├── routes/
│   ├── __init__.py
│   └── order_routes.py      # HTTP layer — declares endpoints, delegates to service
└── services/
    ├── __init__.py
    └── order_service.py     # Business logic — all CRUD operations
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/order-service.git
cd order-service
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

Server will start at: `http://localhost:8000`  
Interactive API docs: `http://localhost:8000/docs`

---

## 📡 API Reference

### Base URL

```
http://localhost:8000
```

### Endpoints

| Method   | Endpoint          | Description                        | Status Code |
|----------|-------------------|------------------------------------|-------------|
| `GET`    | `/health`         | Liveness probe                     | 200         |
| `POST`   | `/orders/`        | Create a new order                 | 201         |
| `GET`    | `/orders/`        | List all orders (filterable)       | 200         |
| `GET`    | `/orders/{id}`    | Get a single order by UUID         | 200         |
| `PUT`    | `/orders/{id}`    | Update order status                | 200         |
| `DELETE` | `/orders/{id}`    | Delete an order                    | 200         |

---

### 📥 Create Order — `POST /orders/`

**Request Body**

```json
{
  "user_id": 42,
  "items": ["Widget A", "Gadget B"],
  "total_price": 99.99
}
```

**Response `201 Created`**

```json
{
  "id": "a3f1c8e2-...",
  "user_id": 42,
  "items": ["Widget A", "Gadget B"],
  "total_price": 99.99,
  "status": "pending",
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

---

### 📋 List Orders — `GET /orders/`

**Optional query parameter:**

```
GET /orders/?status=delivered
```

Allowed values: `pending` · `confirmed` · `shipped` · `delivered`

---

### ✏️ Update Order Status — `PUT /orders/{id}`

**Request Body**

```json
{
  "status": "confirmed"
}
```

---

## 📐 Order Schema

| Field         | Type            | Constraints              |
|---------------|-----------------|--------------------------|
| `id`          | UUID            | Auto-generated           |
| `user_id`     | int             | Required, `> 0`          |
| `items`       | list of strings | Required, non-empty      |
| `total_price` | float           | Required, `> 0`          |
| `status`      | enum (string)   | `pending` (default)      |
| `created_at`  | datetime (UTC)  | Auto-generated           |
| `updated_at`  | datetime (UTC)  | Auto-updated on change   |

### Order Status Lifecycle

```
pending → confirmed → shipped → delivered
```

---

## ⚠️ Error Handling

| Scenario                    | HTTP Status | Example Detail                              |
|-----------------------------|-------------|---------------------------------------------|
| Order not found             | `404`       | `"Order with id '...' not found"`           |
| Same-status update          | `400`       | `"Order is already in 'confirmed' status"`  |
| Invalid field values        | `422`       | Pydantic validation detail (automatic)      |

---

## 🔧 Configuration

### CORS

Configured in `main.py`. For production, replace the wildcard with your actual frontend origin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],  # ← restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Logging

Structured logging is enabled by default at `INFO` level.  
Format: `YYYY-MM-DD HH:MM:SS | LEVEL | module | message`

To change the log level, update `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # or WARNING, ERROR
```

---

## 🔄 Swapping the Database

The DB layer is fully isolated. To replace the in-memory dict with PostgreSQL:

1. Update `database/in_memory_db.py` to return an async SQLAlchemy session
2. Update `services/order_service.py` to use ORM queries
3. Routes and models remain **completely unchanged**

---

## 📦 Dependencies

| Package     | Version    | Purpose                  |
|-------------|------------|--------------------------|
| `fastapi`   | ≥ 0.111.0  | Web framework            |
| `uvicorn`   | ≥ 0.29.0   | ASGI server              |
| `pydantic`  | ≥ 2.7.0    | Data validation          |

---

## 🛠️ Development Tips

- Visit `http://localhost:8000/docs` for the **Swagger UI** — try every endpoint interactively
- Visit `http://localhost:8000/redoc` for **ReDoc** documentation
- All UUIDs are auto-generated — copy them from create responses to use in other requests

---

## 📄 License

MIT License — free to use, modify, and distribute.
