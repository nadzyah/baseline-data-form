# Baseline Data Form

Baseline Data Form is a django web application that allows you to collect baseline data from your customers using yaml fields that you want the customers to fill.

## Installation

Clone the repo, then install the requirements:

```bash
pip3 install -r requirements.txt
```

Keep in mind that here we're using PostgreSQL database instead of SQLite, so you need to install and configure it.

Once you've installed PostgreSQL, edit `NAME`, `USER` and `PASSWORD` fields in DATABASES variable in `settings.py`

If you want to revert to SQLite, set the next value for DATABASES variable:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Once you’ve configured one of the databases, run the next commands:

```bash
python3 ./manage.py migrate
python3 ./manage.py runserver 0.0.0.0:<port>
```

Now you can connect to your server via HTTP: `http://<your_IP>:<port>/`

## Usage

Go to the `http://<your_IP>:<port>/register/` and create a new web form for your customer's organization.

Each organization is stored with its UUID that is used in all URLs that are associated with the organization. Thus customer won't be able to access the web-pages of another one without knowing the exactly UUID of another organization.

Use the web page at `http://<your_IP>:<port>/register/<uuid>/` to edit the form.

To get the last saved version of the yaml file in plain text use `http://<your_IP>:<port>/register/<uuid>/yamldata`

## Customisation

If you want to customize the forms, edit `home.html` file.

To get more information about the editor see [https://github.com/json-editor/json-editor](https://github.com/json-editor/json-editor)
