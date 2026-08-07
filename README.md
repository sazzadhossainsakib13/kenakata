# KenaKata (কেনাকাটা) 🇧🇩🛍️

> **Bangladesh's Premium E-Commerce Marketplace & Unified Point-of-Sale (POS) Retail Platform**

[![Render Deployment](https://img.shields.io/badge/Render-Live_Demo-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://kenakata-o6l6.onrender.com/)
[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

---

## 🌐 Live Production URL & Default Credentials

- **Live URL**: [https://kenakata-o6l6.onrender.com/](https://kenakata-o6l6.onrender.com/)
- **Superuser Admin Credentials**:
  - **Username / Email**: `admin` or `admin@kenakata.com`
  - **Password**: `admin1234`
  - **Admin Panel**: `https://kenakata-o6l6.onrender.com/admin/`
  - **POS Terminal**: `https://kenakata-o6l6.onrender.com/pos/terminal/`

---

## 🌟 About The Project

**KenaKata** (built under **SazzCommerce**) is an enterprise-ready, all-in-one e-commerce and retail POS ecosystem tailored specifically for Bangladesh. It seamlessly connects a modern customer-facing online storefront with an in-store physical POS terminal, providing unified inventory, analytics, and sales reporting across both online orders and offline retail cash registers.

---

## ✨ Core Features & Capabilities

### 🛍️ Online Customer Storefront
- **Dynamic Catalog & Category Engine**: 30+ categories and subcategories (Electronics, Men's Fashion, Women's Fashion, Groceries, Sports, etc.).
- **Smart Image Fallback**: Category-aware high-resolution CDN product imagery and vector SVG placeholders ensure zero broken images.
- **Universal Multi-Method Login**: Customers can log in using their **Username**, **Gmail/Email**, or **Bangladeshi Mobile Number** (`01XXXXXXXXX`).
- **Interactive Cart & Wishlist**: Persistent user sessions, item quantity adjustments, and dynamic coupon codes (`EID2026`, `BDDEAL`, `HACKATHON10`).
- **Cash on Delivery (COD) Checkout**: Built-in Bangladesh division/district selection with automated delivery charges (Inside Dhaka vs. Outside Dhaka).
- **Customer Dashboard**: Track live order status (`Pending`, `Processing`, `Delivered`, `Cancelled`), view itemized receipts, and leave product reviews.

### 🏢 Integrated Point-of-Sale (POS) & Retail Back-Office
- **Cashier Terminal Interface**: Fast barcode scanning, live stock deduction, quantity counters, and split payment methods (Cash, bKash, Nagad, Card).
- **2-Category Sales History**: Unified dashboard clearly categorizing sales into **Offline POS Transactions** and **Online Web Orders** with full product breakdowns, revenue summaries, and cash drawer management.
- **Inventory & Stock Management**: Low-stock alerts, SKU/barcode generation, and real-time inventory ledger tracking.
- **Thermal & Digital Receipts**: Instant receipt print generation for in-store customers.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend Framework** | Python 3.10+, Django 5.0+ |
| **Frontend UI** | HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), Bootstrap 5.3, Bootstrap Icons |
| **Static & Media Serving** | WhiteNoise 6.6+ with high-performance production caching |
| **Database** | SQLite 3 (Local Development) / PostgreSQL Ready via `DATABASE_URL` (Production) |
| **WSGI Server** | Gunicorn 21.2+ |
| **Localization** | BDT (৳) currency formatting, Bangladeshi timezone (`Asia/Dhaka`), 8 administrative divisions |

---

## 📁 Project Architecture

```text
kenakata/
├── accounts/          # User authentication, profiles, mobile validation, and addresses
├── cart/              # Cart state management, session handling, and coupon system
├── catalog/           # Products, categories, brands, specifications, banners & seed commands
├── core/              # Homepage, global context processors, search, and error views
├── dashboard/         # Customer order management & merchant staff dashboard
├── orders/            # Checkout processing, COD fulfillment, and order tracking
├── pos/               # Cashier terminal, sales history (Offline vs. Online), and receipts
├── reviews/           # Verified buyer reviews, rating calculation, and feedback
├── sazzcommerce/      # Django settings, WSGI auto-boot seeding, and URL routing
├── static/            # Design system CSS (base.css), JS scripts, and SVG placeholders
├── templates/         # Modular Django templates (includes, core, catalog, pos, dashboard)
├── wishlist/          # Saved customer wishlist items
├── build.sh           # Cloud build script (migrations, collectstatic, seed_data)
├── render.yaml        # Render.com Infrastructure-as-Code blueprint
└── requirements.txt   # Production dependencies
```

---

## 🚀 Local Development Setup

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/sazzadhossainsakib13/kenakata.git
   cd kenakata
   ```

2. **Create & Activate Virtual Environment**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations & Seed Demo Catalog**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py seed_data
   ```

5. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Open in Browser**
   - Marketplace Storefront: `http://127.0.0.1:8000/`
   - Admin Back-Office: `http://127.0.0.1:8000/admin/` (Login: `admin` / `admin1234`)
   - POS Terminal: `http://127.0.0.1:8000/pos/terminal/`

---

## ☁️ Deployment Guide (Render.com)

1. Fork or push this repository to GitHub.
2. Log in to [Render.com](https://render.com/) and click **New > Web Service**.
3. Connect your `kenakata` GitHub repository.
4. Configure the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn sazzcommerce.wsgi:application`
5. (Optional) Add a PostgreSQL database and set the `DATABASE_URL` environment variable.
6. Click **Deploy Web Service**.

---

## 👤 Author & Maintainer

**Sazzad Hossain Sakib**
- GitHub: [@sazzadhossainsakib13](https://github.com/sazzadhossainsakib13)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
