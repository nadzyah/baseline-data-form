# Baseline Data Form

Baseline Data Form is a django web application that allows you to collect baseline data from your customers using yaml fields that you want the customers to fill.

## Install

Clone the repo, then execute the next commands:

```bash
pip3 install -r requirements.txt
python3 ./manage.py runserver 0.0.0.0:<port>
```

Keep in mind that here we're using PostreSQL database instead of SQLite, so you need to install and configure it.
If you want revert to SQLite, edit `settings.py` file in `sourcedata/`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Then run `python3 ./manage.py migrate`

Now you can connect to your server via HTTP: `http://<your_IP>:<port>/`

## Usage

Go to the `http://<your_IP>:<port>/register/` and create a new web form for your customer's organization.

Each organization is stored with its UUID that is used in all URLs that are associated with the organization. Thus the customer won't be able to access the web-pages of another one without knowing the exactly UUID of another organization.

Use the web page at `http://<your_IP>:<port>/<uuid>/` to edit the form.

To get the latest version of the yaml file in plain text use `http://<your_IP>:<port>/<uuid>/yamldata`

## Customisation

To customize the forms edit `home.html` file in `main/templates/`. To get more information see [https://github.com/json-editor/json-editor](https://github.com/json-editor/json-editor)
