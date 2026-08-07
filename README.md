# KenaKata (SazzCommerce) 🇧🇩🛍️

> **Bangladesh's Premium E-Commerce Marketplace & Merchant POS Platform**

[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

---

## 🌟 Overview

**KenaKata (SazzCommerce)** is an all-in-one, modern e-commerce marketplace and Point of Sale (POS) store management system tailored for seamless online shopping and local merchant operations in Bangladesh. Built with **Django**, **Python**, and **Bootstrap 5**, it provides an intuitive consumer shopping experience alongside a robust back-office system for order fulfillment, inventory tracking, and POS sales.

---

## ✨ Key Features

### 🛍️ Customer Storefront
- **Product Catalog & Filtering**: Search and filter products by category, price, brand, and rating.
- **Dynamic Cart & Wishlist**: Real-time cart updates, item counters, and session-persistent wishlists.
- **Seamless Checkout**: Multi-step checkout process with **Cash on Delivery (COD)** support and shipping address management.
- **Product Reviews & Ratings**: User submission and aggregate rating score displays.
- **Customer Dashboard**: View order history, profile details, and order status tracking.

### 🏢 Merchant & POS Dashboard
- **Point of Sale (POS) System**: Quickly generate in-person transactions and issue receipts.
- **Order Management**: Process, update status (Pending, Processing, Completed, Cancelled), and track nationwide deliveries.
- **Inventory & Catalog Control**: Add, edit, and categorize products with image management.
- **Sales Analytics**: Real-time statistics on revenue, items sold, and top products.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Django 5.0+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Database**: SQLite3 (Development) / PostgreSQL compatible
- **Design & Typography**: Custom Glassmorphism UI, Google Fonts (*Hind Siliguri*, *Inter*)

---

## 🚀 Quick Start Guide

### Prerequisites

Ensure you have the following installed on your machine:
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Sazz-commerce.git
   cd Sazz-commerce/sazzcommerce
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. Open your browser and navigate to `http://127.0.0.1:8000/`

---

## 📁 Project Architecture

```text
sazzcommerce/
├── accounts/          # User authentication, profiles & authorization
├── cart/              # Shopping cart & session management
├── catalog/           # Products, categories, and inventory models
├── core/              # Core pages, homepage, search, & global assets
├── dashboard/         # Customer & merchant management dashboard
├── orders/            # Checkout, order processing, and tracking
├── pos/               # Point-of-Sale merchant interface
├── reviews/           # Product ratings & user review system
├── sazzcommerce/      # Project settings, URLs, & WSGI config
├── static/            # CSS, JavaScript, and asset files
├── templates/         # Modular HTML templates
└── wishlist/          # Saved user products
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git checkout -b feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
