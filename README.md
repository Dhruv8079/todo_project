# TaskFlow — Django To-Do List Application

A professional, full-stack To-Do List web app built with **Django 6.1**, **Python**, **Bootstrap 5**, plain **JavaScript** and **CSS**. It includes authentication, full task CRUD, dashboard statistics, search/filtering, pagination, dark mode and an admin panel.

---

## Features

### Authentication
- Register, login and logout (Django's built-in auth + PBKDF2 password hashing)
- Every task is scoped to its owner; other users' tasks return **404** even with a guessed URL
- Profile page with account info and personal statistics
- Anonymous visitors are redirected to the login page (`@login_required` / `LoginRequiredMixin`)
- Logout is POST-only with CSRF protection (Django 5+ requirement)

### Tasks (CRUD)
- Create, view, edit and delete tasks (delete asks for confirmation)
- Toggle **completed / reopened** from the dashboard, detail page or completed list
- Priority: **Low / Medium / High**
- Categories: **Work / Personal / Study / Other**
- Optional due date, auto `created_at` and `updated_at`
- `is_overdue` and `completion_percentage` model properties

### Dashboard
- Statistic cards: total, completed, pending, overdue
- Completion progress bar and percentage
- Search by title/description, filter by priority and category
- Pagination (9 cards per page)
- Empty states and Django messages for every action

### UI
- Responsive sidebar (offcanvas on mobile), top bar, Bootstrap 5 cards and badges
- Dark-mode toggle persisted in `localStorage` and seeded from the OS preference
- Accessible labels, focus styles and reduced-motion support

### Admin
- Task admin with list display, filters, search, date hierarchy and collapsible fieldsets
- User admin extended with a task inline and a task counter

---

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12+ / Django 6.1.2 |
| Database | SQLite (dev), PostgreSQL-ready via `DATABASES` |
| Templates | Django Template Language |
| Frontend | HTML5, CSS3, vanilla JavaScript, Bootstrap 5.3 |
| Icons | Font Awesome 6 |

---

## Project structure

```
django/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
├── todo_project/              # project package
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── tasks/                     # application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_demo.py
│   └── migrations/
├── templates/                 # project-wide templates
│   ├── base.html
│   ├── registration/
│   │   ├── login.html
│   │   └── register.html
│   └── tasks/
│       ├── dashboard.html
│       ├── completed_tasks.html
│       ├── task_form.html
│       ├── task_detail.html
│       ├── task_confirm_delete.html
│       └── profile.html
├── static/
│   ├── css/style.css
│   └── js/script.js
└── (cricket/, env/, venv/ are unrelated legacy folders)
```

---

## Setup (Windows PowerShell)

Run every command from the folder that contains `manage.py`
(`C:\Users\Lenovo\Desktop\django` in this workspace).

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

Command Prompt alternative: `venv\Scripts\activate.bat`
macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Apply migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 4. Create an admin account

```powershell
python manage.py createsuperuser
```

### 5. (Optional) Load sample tasks

Creates the user **demo / demo12345** with 10 realistic tasks (including overdue and completed ones):

```powershell
python manage.py seed_demo
```

### 6. Run the development server

```powershell
python manage.py runserver
```

### 7. Open the app

| Page | URL |
|---|---|
| Dashboard | http://127.0.0.1:8000/ |
| Login | http://127.0.0.1:8000/accounts/login/ |
| Register | http://127.0.0.1:8000/accounts/register/ |
| Admin | http://127.0.0.1:8000/admin/ |

---

## Routes

| URL | Name | Purpose |
|---|---|---|
| `/` | `tasks:dashboard` | Stats + task list |
| `/search/?q=` | `tasks:task-search` | Search title/description |
| `/priority/<low\|medium\|high>/` | `tasks:task-by-priority` | Filter by priority |
| `/category/<work\|personal\|study\|other>/` | `tasks:task-by-category` | Filter by category |
| `/completed/` | `tasks:completed-tasks` | Completed tasks |
| `/profile/` | `tasks:profile` | Profile + stats |
| `/task/create/` | `tasks:task-create` | Create (GET/POST) |
| `/task/<pk>/` | `tasks:task-detail` | Detail |
| `/task/<pk>/update/` | `tasks:task-update` | Edit (GET/POST) |
| `/task/<pk>/delete/` | `tasks:task-delete` | Confirm + delete (POST) |
| `/task/<pk>/complete/` | `tasks:task-complete` | Toggle completion (POST) |
| `/accounts/login/` | `login` | Login |
| `/accounts/logout/` | `logout` | Logout (POST) |
| `/accounts/register/` | `register` | Registration |

---

## Data model

| Field | Type | Notes |
|---|---|---|
| `user` | FK → `User` | `on_delete=CASCADE` |
| `title` | `CharField(200)` | required |
| `description` | `TextField` | optional |
| `category` | `CharField` | work / personal / study / other (default `other`) |
| `priority` | `CharField` | low / medium / high (default `medium`) |
| `due_date` | `DateTimeField` | optional |
| `is_completed` | `BooleanField` | default `False` |
| `created_at` | `DateTimeField` | `auto_now_add` |
| `updated_at` | `DateTimeField` | `auto_now` |

Ordering: `-due_date, -created_at`.

---

## Tests

```powershell
python manage.py test tasks
```

38 tests cover models, form validation, registration/login, per-user authorization, CRUD, complete/reopen, search, filters, dashboard statistics and the admin pages.

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: No module named 'django'` | Virtual env not activated — run `.\venv\Scripts\Activate.ps1` and `pip install -r requirements.txt` |
| `source code string cannot contain null bytes` | A `.py` file was saved as UTF-16. Re-save it as UTF-8 (in PowerShell use `Set-Content -Encoding utf8`, never plain `>` redirect) |
| `No module named 'todo_project'` | Run `manage.py` from the folder that contains it |
| `Reverse for '...' not found` | Check `app_name = 'tasks'` in `tasks/urls.py`; namespaced names need the `tasks:` prefix |
| `CSRF verification failed` | Add `{% csrf_token %}` to the form and submit via POST from the same site |
| Static files 404 | Confirm `STATICFILES_DIRS = [BASE_DIR / 'static']` and that `static/css/style.css` exists. In production run `python manage.py collectstatic` |
| `no such table: tasks_task` | Run `python manage.py migrate` |
| Styles look stale | Hard refresh (`Ctrl+F5`) — the browser caches CSS |
| 403 on logout | Django 5+ requires POST; the sidebar/profile forms already send a CSRF-protected POST |
| Login loops back to `/accounts/login/` | `LOGIN_REDIRECT_URL` must be `tasks:dashboard` |

---

## Production checklist

1. `DEBUG = False`, set `ALLOWED_HOSTS` to your domains.
2. Move `SECRET_KEY` to an environment variable (`os.environ["DJANGO_SECRET_KEY"]`).
3. Use PostgreSQL (`ENGINE=django.db.backends.postgresql`, plus `psycopg[binary]`).
4. Serve static files with WhiteNoise or a CDN, and run `collectstatic`.
5. Enable HTTPS, `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, and HSTS.
6. Run behind gunicorn/uvicorn + nginx; never use `runserver` in production.
7. Back up the database regularly.

Example production settings fragment:

```python
import os
DEBUG = False
ALLOWED_HOSTS = ['example.com', 'www.example.com']
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

---

## License

MIT — free to use, modify and distribute.
