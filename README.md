# ClinicSync API

This is the backend that powers ClinicSync, a clinic management system that offers various modules to ensure smooth day to day operations of a clinic facility.
Some of the modules in development include:

- User authentication & authorization.
- Onboarding of new clinics.
- Patient and health records managment.
- Doctor appointment and check up reservations.
- Doctor & staff management.
- Stock(medicine) & inventory management.
- Order & sales management.

#### TECH STACK
The backend is built using the following technologies:
- Django
- Django REST Framework
- Postgres
- SendGrid
- Celery
- Redis

#### FRONTEND

The frontend part is built using Vue3(Composition API) and styled using Tailwind CSS.
The repo for that is [found here.](https://github.com/nicksonlangat/medical_clinic_management_system.git)

#### LOCAL DEV SETUP

To set up this part on your local machine, follow the steps below:
- Install [Python](https://www.python.org/downloads/)
- Install [Postgres](https://www.postgresql.org/download/) and create a new database, call it `clinic_db` for example.

- Install [Redis](https://redis.io/downloads/)
- Create a working directory on your machine.
- Clone this repo `https://github.com/nicksonlangat/clinicsync_api.git`
- Create a virtual environment `virtualenv env`
- Activate the virtual environment `source env/bin/activate`
- Install project's dependencies `pip install -r requirements.txt`
- Create a `.env` file and add the following values in it:

    ```bash
    SECRET_KEY=<SECRET-KEY>
    DEBUG=on
    DB_NAME=<DB-NAME>
    DB_USER=<DB-USER>
    DB_PASSWORD=<DB-PASSWORD>
    DB_HOST=localhost
    DB_PORT=5432
    SENDGRID_API_KEY=<SENDGRID-API-KEY>
    EMAIL_HOST="smtp.sendgrid.net"
    EMAIL_HOST_USER="apikey" # this is exactly the value 'apikey'
    EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    AWS_ACCESS_KEY_ID=
    AWS_SECRET_ACCESS_KEY=
    AWS_STORAGE_BUCKET_NAME=
    AWS_QUERYSTRING_AUTH=False
    ```
- Run database migrations  `python manage.py migrate`
- Spin the server `python manage.py runserver 8005`
