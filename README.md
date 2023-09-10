Linux:
1. Create virtualenv
2. `pip install -r requirements.txt`

Initialize web_app:
3. `python web/web_project/manage.py migrate --pythonpath . --fake 0001`
4. `python web/web_project/manage.py migrate --pythonpath .`
4. `python web/web_project/manage.py runserver --pythonpath .`
