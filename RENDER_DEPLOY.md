# 🚀 Render.com Deployment Guide for KenaKata

> **Deploy your Django + POS marketplace with free SSL and automatic GitHub integration on Render in 3 minutes.**

---

## 📋 Quick Setup (Step-by-Step)

### 1. Sign in to Render
* Go to [https://render.com/](https://render.com/) and click **Get Started** or **Log In**.
* Select **Sign in with GitHub** (`sazzadhossainsakib13`).

---

### 2. Create Web Service
1. Click the **New +** button at top right ➔ Select **Web Service**.
2. Choose **Build and deploy from a Git repository**.
3. Select your repository: **`sazzadhossainsakib13/kenakata`**.

---

### 3. Fill in Configuration Settings
| Field | Value |
|---|---|
| **Name** | `kenakata` *(or any custom name)* |
| **Region** | `Singapore` *(Fastest for Bangladesh)* |
| **Branch** | `main` |
| **Root Directory** | *(leave blank)* |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` *(or `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`)* |
| **Start Command** | `gunicorn sazzcommerce.wsgi:application` |
| **Instance Type** | **Free** |

---

### 4. Deploy!
1. Click **Create Web Service** at the bottom.
2. Render will automatically build dependencies, migrate tables, collect static assets, and start Gunicorn.
3. In ~2 minutes, your live store will be online with free SSL at:
   👉 **`https://kenakata.onrender.com`**

---

### 👤 Creating Admin Superuser on Render
If you need an admin account on Render:
1. In your Render dashboard, click your `kenakata` service ➔ Go to the **Shell** tab.
2. Type:
   ```bash
   python manage.py createsuperuser
   ```
3. Enter your username, email, and password. You can now log into `/admin/` on your live site!
