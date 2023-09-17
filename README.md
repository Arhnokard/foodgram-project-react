## Foodgram-project-react

### Описание:
Сервис, который позволяет создавать/просматривать рецепты блюд, 
подписываться на авторов, добавлять рецепты в избранное и в список покупок. 
Список покупок выгружается в виде файла (shopping-list.txt), в котором сохранены все
ингредиенты для рецептов из списка покупок.

### Используемые технологии
- Django
- Django Rest Framework
- Docker
- Docker-compose
- Gunicorn
- Nginx
- PostgreSQL

### Workflow
- **tests:** Проверка кода на соответствие PEP8.
- **push Docker image to Docker Hub:** Сборка и публикация образа на DockerHub.
- **deploy:** Автоматический деплой на боевой сервер при пуше в главную ветку main.
- **send_massage:** Отправка уведомления в телеграм-чат.

### Для работы с Workflow добавить в Secrets GitHub переменные окружения:
```
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

SECRET_KEY=<код для settings>
ALLOWED_HOSTS=<список разрешенных хостов>

DOCKER_PASSWORD=<пароль DockerHub>
DOCKER_USERNAME=<имя пользователя DockerHub>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<ID своего телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего бота>
```

### Запуск проекта

Cоздать в корневой папке и заполнить .env  c переменными:
```
SECRET_KEY
ALLOWED_HOSTS
DB_NAME
POSTGRES_USER
POSTGRES_PASSWORD
DB_HOST
DB_PORT
```

Из папки infra/ развернуть контейнеры при помощи docker-compose:
```
docker-compose up -d --build
```
Выполнить миграции:
```
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
```
Создать администратора:
```
sudo docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
```
Собрать статику:
```
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic --no-input
```
Заполнить базу ингредиентами и тегами (опционально):
```
sudo docker compose -f docker-compose.yml exec backend python manage.py add_ingredients
sudo docker compose -f docker-compose.yml exec backend python manage.py add_tags
```
Остановка проекта:
```
docker-compose down
```

#### REST API
Подробная документация API будет доступна по адресу - http://<IP-адрес вашего сервера>/api/docs/

#### Автор:
Поздняков Евгений - [https://github.com/Arhnokard](https://github.com/Arhnokard)