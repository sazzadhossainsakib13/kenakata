# 🐍 PythonAnywhere Deployment Guide for KenaKata

Deploying **KenaKata** on **PythonAnywhere** takes only 5 minutes. Follow this exact step-by-step guide.

---

## 📋 Step 1: Create a Free Account
1. Go to [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/) and register for a free **"Beginner"** account.
2. Remember your **username** (your live URL will be `https://yourusername.pythonanywhere.com`).

---

## 💻 Step 2: Open a Bash Console & Clone the Code

1. In your PythonAnywhere dashboard, click on **Consoles** tab -> click **Bash**.
2. In the terminal, run the following commands:

```bash
# 1. Clone the GitHub repository
git clone https://github.com/sazzadhossainsakib13/kenakata.git

# 2. Navigate to project folder
cd kenakata

# 3. Create a Python 3.10 virtual environment
mkvirtualenv --python=/usr/bin/python3.10 kenakata-venv

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migrations & collect static files
python manage.py migrate
python manage.py collectstatic --noinput

# 6. Create your Superuser / Admin account
python manage.py createsuperuser
```

---

## 🌐 Step 3: Configure the Web App

1. Go back to your PythonAnywhere dashboard and click on the **Web** tab.
2. Click **Add a new web app**.
3. Choose **Manual configuration** (do **NOT** select Django, select *Manual configuration*).
4. Choose **Python 3.10**.
5. Click **Next** to complete the wizard.

---

## ⚙️ Step 4: Configure Virtualenv & Paths

In the **Web** tab, scroll down and fill in these exact sections:

### 1. Code Section:
* **Source code**: `/home/yourusername/kenakata`
* **Working directory**: `/home/yourusername/kenakata`

### 2. Virtualenv Section:
* **Virtualenv**: `/home/yourusername/.virtualenvs/kenakata-venv`
*(Or simply type `kenakata-venv` and press checkmark)*

### 3. Static files Section:
Add these 2 rows in the Static files table:

| URL | Directory |
|---|---|
| `/static/` | `/home/yourusername/kenakata/staticfiles` |
| `/media/` | `/home/yourusername/kenakata/media` |

*(Replace `yourusername` with your actual PythonAnywhere username)*

---

## 📝 Step 5: Edit the WSGI Configuration File

1. In the **Web** tab, under the **Code** section, click on the **WSGI configuration file** link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`).
2. Delete everything inside that file and paste the following:

```python
import os
import sys

# Path to your project directory
path = '/home/yourusername/kenakata'
if path not in sys.path:
    sys.path.append(path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'sazzcommerce.settings'

# Load the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
*(Remember to replace `yourusername` with your real username on line 5)*

3. Click **Save** (top right).

---

## 🚀 Step 6: Reload and Visit Your Live Site!

1. Go back to the **Web** tab.
2. Click the big green button: **Reload yourusername.pythonanywhere.com**.
3. Open your browser and navigate to:
   * **Marketplace**: `https://yourusername.pythonanywhere.com/`
   * **POS Terminal**: `https://yourusername.pythonanywhere.com/pos/terminal/`
   * **POS Dashboard**: `https://yourusername.pythonanywhere.com/pos/`
   * **Admin Panel**: `https://yourusername.pythonanywhere.com/admin/`

🎉 **Your KenaKata store is now LIVE for the world to see!**
