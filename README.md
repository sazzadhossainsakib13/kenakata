# KenaKata (SazzCommerce) 🇧🇩🛍️

> **Bangladesh's Premium E-Commerce Marketplace & Merchant POS Platform**

[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

---

## 🌟 Overview

**KenaKata** (built under **SazzCommerce**) is a full-featured, modern e-commerce marketplace and integrated Point of Sale (POS) store management system. Specifically crafted for online shopping and local retail operations in Bangladesh, it combines a sleek customer-facing marketplace with a powerful merchant back-office system.

---

## ✨ Key Features

### 🛍️ Customer Storefront
- **Dynamic Product Catalog**: Browse products with multi-category filtering, instant search, price ranges, and ratings.
- **Cart & Wishlist Management**: Interactive shopping cart with persistent sessions, tax/shipping calculations, and wishlist save functionality.
- **Checkout & Cash on Delivery (COD)**: Custom checkout flow supporting local Bangladeshi shipping addresses and COD payment method.
- **Ratings & Reviews**: User product reviews, star ratings, and verified buyer badges.
- **Customer Account Portal**: View past orders, track live shipment status, and update profile details.

### 🏢 Merchant & POS Dashboard
- **Point of Sale (POS) Interface**: Fast, terminal-style in-person sale creation, stock validation, and instant receipt generation.
- **Order Fulfillment Center**: Track, filter, and update order statuses (`Pending`, `Processing`, `Completed`, `Cancelled`).
- **Inventory & Product Management**: Add, update, and categorize items with multi-image support and stock monitoring.
- **Sales Analytics & Insights**: Key performance metrics including total revenue, order volume, and top-selling products.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Django 5.0+
- **Frontend**: HTML5, Vanilla CSS, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Database**: SQLite3 (Development) / PostgreSQL Ready (Production)
- **Typography & UI**: Custom Glassmorphism styling, Google Fonts (*Hind Siliguri*, *Inter*)

---

## 📁 Repository Structure

```text
kenakata/
├── accounts/          # User authentication, authorization & profiles
├── cart/              # Cart state management & checkout sessions
├── catalog/           # Products, categories, brands, & inventory models
├── core/              # Homepage, search, context processors, global views
├── dashboard/         # Customer portal & merchant admin dashboard
├── orders/            # Order creation, processing, & status tracking
├── pos/               # Merchant Point-of-Sale terminal & receipts
├── reviews/           # Product rating & customer review system
├── sazzcommerce/      # Main Django project settings, URLs & WSGI
├── static/            # Static assets (CSS, JS, custom icons)
├── templates/         # Modular HTML5 Jinja/Django templates
└── wishlist/          # Saved user items
```

---

## 🚀 Quick Start Guide

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/sazzadhossainsakib13/kenakata.git
   cd kenakata
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access the App**
   Open your browser and navigate to:
   - **Marketplace**: `http://127.0.0.1:8000/`
   - **Django Admin**: `http://127.0.0.1:8000/admin/`

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👤 Author

**Sazzad Hossain Sakib**
- GitHub: [@sazzadhossainsakib13](https://github.com/sazzadhossainsakib13)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

