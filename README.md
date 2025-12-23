# OliveGarden Django Project

OliveGarden is a Django 5.2 project with a small e-commerce flow: products,
accounts, and a session-backed cart.

## Features
- Product catalog with slug-based detail pages.
- Session cart with quantity updates and stock checks.
- Custom user model and sign up / sign in / sign out views.
- Media uploads for product images.

## Tech Stack
- Python + Django 5.2
- SQLite (default `db.sqlite3`)

## Requirements
See `requirements.txt` for the pinned dependencies.

## Local Setup
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations:

```bash
python manage.py migrate
```

4. (Optional) Create an admin user:

```bash
python manage.py createsuperuser
```

5. Run the server:

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

## Routes
- `/` - Home page.
- `/products/` - Product list.
- `/products/<slug>/` - Product detail.
- `/cart/` - Cart detail.
- `/cart/add/<product_id>` - Add to cart.
- `/cart/update/<product_id>` - Update cart quantity.
- `/cart/remove/<product_id>` - Remove from cart.
- `/accounts/sign_up` - Sign up.
- `/accounts/sign_in` - Sign in.
- `/accounts/sign_out` - Sign out.
- `/admin/` - Django admin.

## App Structure
- `core`: Home page.
- `products`: Product model, list, and detail views.
- `accounts`: Custom user model + auth views.
- `cart`: Session cart logic and views.

## Media and Static Files
- Media uploads are stored in `media/` and served in development when
  `DEBUG=True`.
- Static files are configured via `STATIC_URL` and `STATICFILES_DIRS`.

## Notes
- `AUTH_USER_MODEL` is set to `accounts.User`.
- Authentication accepts username or email at login.

## Screenshots
Add screenshots in `docs/screenshots/` and reference them here as they
become available.
