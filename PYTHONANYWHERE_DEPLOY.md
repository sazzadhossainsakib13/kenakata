# 🐍 PythonAnywhere Deployment Guide for sazzad

> **Your Live URL**: [https://sazzad.pythonanywhere.com/](https://sazzad.pythonanywhere.com/)

---

## 💻 Step 1: Open Bash Console & Run Setup Commands

1. Go to [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/) and log in as **`sazzad`**.
2. Click on the **Consoles** tab and click on **Bash**.
3. Copy and paste the following block into the Bash terminal:

```bash
# 1. Clone your GitHub repository
git clone https://github.com/sazzadhossainsakib13/kenakata.git

# 2. Go into project directory
cd kenakata

# 3. Create Python 3.10 virtual environment
mkvirtualenv --python=/usr/bin/python3.10 kenakata-venv

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run database migrations & collect static files
python manage.py migrate
python manage.py collectstatic --noinput

# 6. Create your Superuser Admin account (enter your desired username/password)
python manage.py createsuperuser
```

---

## 🌐 Step 2: Create the Web App

1. Click on the **Web** tab at the top.
2. Click **Add a new web app**.
3. Choose **Manual configuration** *(Important: Do NOT choose Django, choose "Manual configuration")*.
4. Choose **Python 3.10**.
5. Click **Next** to finish the wizard.

---

## ⚙️ Step 3: Configure Paths & Static Files for `sazzad`

On the **Web** tab page, scroll down and set these exact paths:

### 1. Code Section:
* **Source code**: `/home/sazzad/kenakata`
* **Working directory**: `/home/sazzad/kenakata`

### 2. Virtualenv Section:
* **Virtualenv**: `/home/sazzad/.virtualenvs/kenakata-venv`
*(Or simply type `kenakata-venv` and click the blue checkmark)*

### 3. Static files Section:
Add these **2 exact rows** in the Static files table:

| URL | Directory |
|---|---|
| `/static/` | `/home/sazzad/kenakata/staticfiles` |
| `/media/` | `/home/sazzad/kenakata/media` |

---

## 📝 Step 4: Edit the WSGI Configuration File

1. In the **Web** tab under the **Code** section, click on the **WSGI configuration file** link (`/var/www/sazzad_pythonanywhere_com_wsgi.py`).
2. Delete everything currently inside that file and paste this exact code:

```python
import os
import sys

# Path to your project directory
path = '/home/sazzad/kenakata'
if path not in sys.path:
    sys.path.append(path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'sazzcommerce.settings'

# Load the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

3. Click **Save** (top right).

---

## 🚀 Step 5: Reload and View Your Live Website!

1. Go back to the **Web** tab.
2. Click the green button: **Reload sazzad.pythonanywhere.com**.
3. Visit your live store:
   * 🛍️ **Marketplace**: `https://sazzad.pythonanywhere.com/`
   * 🛒 **Shop & Catalog**: `https://sazzad.pythonanywhere.com/shop/`
   * 🖥️ **POS Terminal**: `https://sazzad.pythonanywhere.com/pos/terminal/`
   * 📈 **Sales History**: `https://sazzad.pythonanywhere.com/pos/sales/`
   * 🛡️ **Django Admin**: `https://sazzad.pythonanywhere.com/admin/`
