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

### MODULE BREAKDOWN

The following is a description of what each module does.

### ACCOUNTS
This module is responsible for the registration authentication and authorization of users in to the platform.
The registration process is multi-step:
- First the user enters their details (email, first_name, last_name, phone_number, password)
- They receive a verification OTP to activate their newly created accounts.
- They then login and proceed to the next step.
- They are taken to a clinic creation screen where they are asked to enter clinic info(name, location, clinic phone_number, clinic_email)
- If all info is correct, the clinic is created with the user as the owner.
- User is taken to their dashboard.

This modules also allows a user to reset their password should they forget it.
- They enter the email address associated with their account.
- They are sent a OTP that they can use to verify identity.
- Next they are asked to set new password.
- The user is redurected to login page.

Some pages for this section are attached.

Register
![register](./screenshots/register.png)

Login
![login](./screenshots/login.png)

Password reset
![reset](./screenshots/reset.png)

### DASHBOARD
The dashboard gives the clinic owner a 360 overview of various sections of their day to day operations. This is shown below:

![dashboard](./screenshots/dashboard.png)


### STOCKS
This module is divided into two:
- Inventory sub module
- Order sub module
##### INVENTORY
This module allows the clinic owner to:
- Upload new products into the inventory
- Bulk upload products from a Microsoft excel sheet
- View all products in the inventory
- Filter and sort products in the inventory
- View inventory analytics in realtime

Here is a video showing a demo of this section. [View ti here](https://www.loom.com/share/e3a924a76d38494c95f6d73fe250409c?sid=94f9b823-cafb-4fc3-a1c7-985145be6eba)


Inventory

![reset](./screenshots/inventory.png)

##### ORDERS

This module allows the clinic owner to:

- Create a new order request.
- Send order request as an email to the vendor/supplier.
- Mark an order as complete, cancelled or pending. Note that marking an order as complete means the clinic has received all order items and the order items get marked individually as received. The reverse is true.
- Mark individual order items as received. Note that marking all individual order items as received will marke the status of the parent order as complete. The opposite is true.


Orders

![reset](./screenshots/orders.png)
