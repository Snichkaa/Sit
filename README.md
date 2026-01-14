# VG Sales Django + PostgreSQL + Jinja2 (Lab Project)

## 1) Prerequisites
- Python 3.10+ (recommended)
- PostgreSQL 13+ running locally

## 2) Setup (Windows PowerShell example)
```powershell
cd .\vg_django_project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Create PostgreSQL database/user
You can do this via pgAdmin or psql. Example SQL:
```sql
CREATE DATABASE vgdb;
CREATE USER vguser WITH PASSWORD 'vgpass';
GRANT ALL PRIVILEGES ON DATABASE vgdb TO vguser;
```

Then edit `vgsite/settings.py` -> DATABASES (NAME/USER/PASSWORD/HOST/PORT).

## 4) Migrate + create admin user
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 5) Load Kaggle CSV into DB
Put your CSV into `data/` and run:
```powershell
python manage.py load_vgsales --path data\Video_Game_Sales_with_Ratings.csv
```

> If your CSV file has a different name, adjust the path.

## 6) Run server
```powershell
python manage.py runserver
```
Open: http://127.0.0.1:8000/

## Notes
- Templates are Jinja2 and located in `catalog/jinja2/catalog/`
- CRUD forms implemented for the "Game" entity: add/edit/delete
