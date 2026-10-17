# Gadget Deluxe — Used iPhone E-Commerce Store

**Focus:** Exclusively used and premium iPhones (**iPhone 14 Pro, iPhone 14 Pro Max, iPhone 15 Pro, iPhone 15 Pro Max, iPhone 16 Pro, iPhone 16 Pro Max**).

---

## 🚀 Tech Stack

- **Backend:** Python 3.12+ / Django 5+
- **Frontend:** Django Templates & Tailwind CSS
- **Database:** Neon PostgreSQL (with SQLite fallback for local development)
- **Static Assets:** WhiteNoise
- **WSGI Server:** Gunicorn
- **Deployment:** Render (`render.yaml` & `build.sh` included)
- **Internationalization:** English & বাংলা (bilingual support with instant switcher)

---

## 📱 Core Features

1. **Focused iPhone Catalog**:
   - Distinct physical unit listings with unique SKUs, Storage, Color, 52-point inspection tests, Condition badges (99% Like New, 95% Excellent, 90% Good), authentic Battery Health %, SIM/eSIM variants, and origin region (LL/A, ZA/A, J/A).
   - Anti-double ordering inventory locking (prevents selling the same physical phone to multiple customers).
2. **Minimalist Apple-Inspired Design**:
   - Clean, fast, mobile-first UI with responsive typography, glassmorphism header, and subtle animations.
3. **Cart & Dynamic Checkout**:
   - Registered user or instant Guest Checkout (no mandatory registration).
   - Dynamic delivery charge calculation (Inside Dhaka ৳100 / Outside Dhaka ৳150).
   - Server-side price and stock validation.
4. **Manual Payment Verification System**:
   - Cash on Delivery (COD)
   - bKash (Sender Number & TrxID)
   - Nagad (Sender Number & TrxID)
   - Rocket (Sender Number & TrxID)
   - Bank Transfer (Direct Deposit Slip/Ref)
   - Dynamic payment instructions & account numbers manageable from Django Admin.
5. **Real-time Visual Order Tracking**:
   - Guest tracking via Order ID + Phone Number or direct secure tracking link.
   - Visual 6-step progress stepper: *Order Placed → Confirmed → Processing → Shipped → Out for Delivery → Delivered*.
6. **Bilingual FAQ & Trust Center**:
   - Answers to common questions regarding battery health, 3uTools testing, TrueTone, warranty, inspection on delivery, and guest orders.
   - Manageable from Admin with both English and Bangla text.
7. **Comprehensive Custom Admin Portal (`/shop-admin/`)**:
   - **Live Analytics & Traffic:** Total page views, daily/weekly/monthly unique visitor counts, and 30-day traffic growth charts.
   - **Cash Flow Tracking:** Real-time revenue tracking across **Cash on Delivery, bKash, Nagad, Rocket, and Bank Transfer**, with Paid vs. Pending Verification breakdown.
   - **Inventory Manager:** Add new iPhone listings, update specifications (storage, color, condition, battery health, SIM type, price, description in EN/BN), upload multiple gallery photos, and quick toggle stock status (*Available / Reserved / Sold*).
   - **Orders & Payment Verification:** Review customer details, copy transaction IDs (TrxID), update fulfillment status (*Pending → Confirmed → Shipped → Delivered*), print invoices, and **Export Orders to CSV**.
   - **Store & Payment Settings:** Change store hotline, WhatsApp, address, and mobile financial account numbers directly from the dashboard.
   - **FAQ Manager:** Full CRUD for bilingual customer FAQs.

---

## 💻 Local Development Setup

### 1. Clone & create virtual environment
```bash
git clone https://github.com/jubaerkhan49/gadget-deluxe-shop.git
cd gadget-deluxe-shop

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup environment variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Run database migrations & seed initial catalog
```bash
python manage.py migrate
python manage.py seed_data
```
> **Default Admin Account:**
> - Username: `admin`
> - Password: `admin123456`

### 5. Start development server
```bash
python manage.py runserver
```
Visit `http://localhost:8000` in your browser.

---

## 🧪 Running Automated Tests

```bash
python manage.py test
```

---

## ☁️ Deployment on Render & Neon PostgreSQL

1. **Database:** Create a PostgreSQL instance on [Neon](https://neon.tech) and copy your `DATABASE_URL`.
2. **Web Service on Render:**
   - Connect this GitHub repository.
   - Runtime: `Python 3`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn gadget_deluxe.wsgi --log-file -`
3. **Environment Variables on Render:**
   - `DATABASE_URL`: `postgresql://<user>:<password>@<host>/<dbname>?sslmode=require`
   - `SECRET_KEY`: `<secure-random-key>`
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com,gadgetdeluxe.shop,www.gadgetdeluxe.shop`
   - `CSRF_TRUSTED_ORIGINS`: `https://*.onrender.com,https://gadgetdeluxe.shop,https://www.gadgetdeluxe.shop`
