### Operating System
- Windows - tested
- Linux - tested

### Setup environment:
1. Create virtualenv
2. `pip install -r requirements.txt`

### Initialize web_app:
3. `python web/web_project/manage.py migrate --pythonpath . --fake web_app 0001`
4. `python web/web_project/manage.py migrate --pythonpath .`
5. `python web/web_project/manage.py runserver --pythonpath .`

### Use the app:
6. Откройте в браузере [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
7. Создайте заказ, введите название заказа и выберите тип вагона
8. Нажмите "Перейти к заказу"
9. Добавьте грузы к заказу, укажите их габариты и вес
10. Нажмите "Расситать расположение грузов"
11. Скачайте созданные чертеж и расчетно-пояснительную записку