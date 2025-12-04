🛒 Multi-Tenant E-Commerce Backend (Django + DRF + JWT)

This project is a multi-tenant e-commerce backend where multiple vendors can host their stores on a shared platform.
Each vendor has their own:

Products

Orders

Customers

Staff

Store Owner

Vendors cannot access each other’s data (strict isolation).
Authentication uses JWT (SimpleJWT), and each token contains:

tenant_id

tenant_domain

role

Role-based access is fully implemented.

🚀 Features
✅ Multi-Tenancy

Each vendor has isolated data

Vendor is detected using:

X-Tenant-Domain: vendor1.example.com


Middleware attaches the vendor to every request

✅ Roles
Role	Permissions
Owner	Full access to products, orders, staff, customers
Staff	Manage products & assigned orders
Customer	Browse products & place/view own orders
✅ Authentication

Register / Login

JWT with tenant info

Custom claims (role + vendor)

✅ CRUD Operations

Products

Orders

Staff assignment

Customer order history (/my/)

✅ Order Functions

Place order

Update status

Assign staff

Customer my orders API

✅ Tenant-Aware Querying

Every queryset filters by vendor = request.tenant.

🏗 Technologies Used

Python 3

Django

Django REST Framework

SimpleJWT

SQLite / PostgreSQL

📦 Installation & Setup
1️⃣ Clone the repository
git clone <your-repo-link>
cd <project-folder>

2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run migrations
python manage.py migrate

5️⃣ Create superuser
python manage.py createsuperuser

6️⃣ Start server
python manage.py runserver

🧩 Multi-Tenancy Implementation

Multi-tenancy is implemented using:

✔ Vendor Model

Each vendor has:

store name

contact

domain or subdomain

owner

✔ Tenant Middleware

Middleware extracts:

X-Tenant-Domain: vendor1.example.com


Then finds the vendor:

request.tenant = Vendor.objects.get(domain=domain)


All queries use:

Model.objects.filter(vendor=request.tenant)

🔐 Role-Based Access

JWT tokens store:

{
  "user_id": 1,
  "role": "owner",
  "tenant_id": 3,
  "tenant_domain": "vendor1.example.com"
}


Permissions:

Owner

✔ manage all products
✔ manage orders
✔ assign staff
✔ view customers
✔ view staff

Staff

✔ manage products
✔ update order status
✔ see orders assigned to them

Customer

✔ view products
✔ place orders
✔ view only their orders

🔑 Authentication APIs
POST /api/auth/register/

Register owner / staff / customer.

POST /api/auth/login/

Returns JWT:

{
  "access": "...",
  "refresh": "..."
}


Headers needed for all APIs:

Authorization: Bearer <token>
X-Tenant-Domain: vendor1.example.com

📘 API Endpoints
🔹 Products
Method	Endpoint	Description
GET	/api/products/	List vendor products
POST	/api/products/	Create product (owner/staff)
GET	/api/products/<id>/	View product
PUT/PATCH	/api/products/<id>/	Update product
DELETE	/api/products/<id>/	Delete product
🔹 Orders
Method	Endpoint	Description
POST	/api/orders/	Create order (customer)
GET	/api/orders/	List orders (owner/staff)
GET	/api/orders/my/	Customer's own orders
PATCH	/api/orders/<id>/status/	Update order status
PATCH	/api/orders/<id>/assign-staff/	Assign staff to order
📦 Sample Payloads
🔹 Register Customer / Staff / Owner
{
  "username": "vendor1_customer1",
  "password": "password123",
  "role": "customer",
  "vendor_domain": "vendor1.example.com"
}

🔹 Login
{
  "username": "vendor1_customer1",
  "password": "password123"
}

🔹 Create Product
{
  "name": "Watch",
  "description": "Waterproof watch",
  "price": "49.99",
  "stock": 10
}

🔹 Create Order
{
  "items": [
    { "product": 1, "quantity": 2 }
  ],
  "address": "123 Street"
}

🔹 Assign Staff
{
  "staff_id": 7
}

🧪 Testing Vendor Isolation

Try accessing vendor2 data with vendor1's token:

GET /api/products/
X-Tenant-Domain: vendor2.example.com
Authorization: Bearer <vendor1_token>


Expected:

403 Forbidden


This confirms multi-tenancy isolation.

📁 Project Structure
/project
    /authentication
    /orders
    /products
    /vendors
    /middleware
    manage.py
    requirements.txt
    README.md

🎯 Conclusion

This backend supports:

✔ Multi-tenant e-commerce
✔ JWT auth
✔ Tenant-based filtering
✔ Role-based access
✔ Staff assignment
✔ Customer order tracking


The following are the payloads
http://127.0.0.1:8000/api/auth/register/

For registering Vendor
// {
//   "username": "owner3",
//   "email": "owner3@store.com",
//   "password": "password123",
//   "role": "owner",
//   "vendor_domain": "vendor3.example.com",
//   "first_name": "Alice3",
//   "last_name": "Owner"
// }



X-Tenant-Domain : is required for creating staff 
For registering Staff
// {
//   "username": "vendor3_staff2",
//   "email": "staff2@vendor3.com",
//   "password": "password123",
//   "role": "staff",
//   "first_name": "Staff",
//   "last_name": "two"
// }

X-Tenant-Domain : is required for creating customer 
For registering Customer
http://127.0.0.1:8000/api/auth/register/ [POST]
{
  "username": "vendor3_customer3",
  "email": "customer3@vendor3.com",
  "password": "password123",
  "role": "customer",
  "first_name": "Customer",
  "last_name": "three"
}



For Login :-
http://127.0.0.1:8000/api/auth/login/ [POST]
{
  "username": "vendor1_customer1",
  "password": "password123"
}




For Creating Products :-
X-Tenant-Domain : is required for creating customer (vendor domain)
Authorization jwt is required
http://127.0.0.1:8000/api/products/ [POST]
{
  "name": "Vendor3 Product C",
  "description": "Eco-friendly product C.",
  "price": "45.99",
  "stock": 35
}


For Customer Placing Order
X-Tenant-Domain : is required for creating customer (vendor domain)
Authorization customer jwt is required
http://127.0.0.1:8000/api/orders/ [POST]
{
    "items": [
        {
            "product": 1,
            "quantity": 2
        },
        {
            "product": 3,
            "quantity": 1
        }
    ],
    "address": "123 Main Street"
}

To see vendor/Store orders :-
X-Tenant-Domain : is required for creating customer (vendor domain)
Authorization owner jwt is required
http://127.0.0.1:8000/api/orders/

To give status for an order :-
http://127.0.0.1:8000/api/orders/1/status/ [PATCH]
{
    "status": "processing"
}

To Assign Staff to particular Order :-
X-Tenant-Domain : is required for creating customer (vendor domain)
Authorization owner jwt is required
http://127.0.0.1:8000/api/orders/1/assign-staff/ [PATCH]
{
    "staff_id": 5
}




