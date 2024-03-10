# resume-scannar-frontend-with-theme
# HireWise.ai
# This is our AI Resume Scanner and Ranking System that rank the appliciant based on the job description provide by the Recruiter.
It is recommended to use virtual environment packages such as virtualenv. Follow the steps below to setup the project:
  - Clone this repository via  `git clone https://github.com/121abhi/resume-scanner.git`
  - Use this command to install required packages `pip install -r requirements.txt`
  - Crate database and change database settings in `settings.py` according to your database. Install appropriate database connector if need.
    - **Mysql**:
       ```
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql', 
                'NAME': 'DB_NAME',
                'USER': 'DB_USER',
                'PASSWORD': 'DB_PASSWORD',
                'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
                'PORT': '3306',
            }
        }
        ```
    - **SQLite**:
      ```
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'mydatabase', # This is where you put the name of the db file. 
                         # If one doesn't exist, it will be created at migration time.
            }
        }
      ```
    - **Others**: See documentation, put appropriate database settings and install connector.
  - Folder Structure JobPortal is Django Project, inside the JobPortal manage.py and my_site(django apps) is present and then execute below commands
  - Generate migration files of the project via terminal: `python manage.py makemigrations`
  - Migrate the project files from terminal: `python manage.py migrate`
  - Create admin user for admin panel from terminal: `python manage.py createsuperuser`. And enter the username, email and password. 
  - Run the project from terminal: `python manage.py runserver`
