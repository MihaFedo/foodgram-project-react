# Foodgram, "Продуктовый помощник" / "Recipe assistant" ![Workflow status](https://github.com/MihaFedo/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

Развернутый проект доступен по адресу: http://suprecipe.sytes.net
Вход для суперюзера: http://suprecipe.sytes.net/admin (lyganin / lyganin)


### Описание дипломного проекта / Graduate project description
Написать онлайн-сервис и API для сайта Foodgram, «Продуктовый помощник». На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Исходники для реализации проекта
В исходном репозитории были заготовлены папки frontend, backend, infra, data и docs:
- в папке frontend находятся файлы, необходимые для сборки фронтенда приложения,
- в папке infra — заготовка инфраструктуры проекта: конфигурационный файл nginx и docker-compose.yml,
- в папке backend пусто - папка для разработки бэкенда продуктового помощника,
- в папке data подготовлен список ингредиентов с единицами измерения,
- в папке docs — файлы спецификации API.

### Локальный запуск проекта и спецификация API
1. В папке infra выполните команду
```
docker-compose up
``` 
При выполнении команды запустятся следующие контейнеры, описанные в docker-compose.yml:
- frontend подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу. 
Проект запустится на адресе http://localhost, увидеть спецификацию API можно по адресу http://localhost/api/docs/
- db подготовит БД postgres
- backend подготовит к работе основной функционал django приложения
- nginx подготовит сервер в соответствии с параметрами из nginx.conf.
2. Подготовить и выполнить миграции для базы данных:
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```
3. Создать суперюзера для проекта:
```
docker-compose exec backend python manage.py createsuperuser
```
4. Собрать файлы статики в отдельную папку:
```
docker-compose exec backend python manage.py collectstatic --no-input
```
5. Наполнить базу данных ингредиентами и единицами измерения можно командой:
```
docker-compose exec backend python manage.py load_csv_file
```

### Команды для запуска приложения в контейнерах на сервере (ВМ Yandex Cloud)
- Войдите на удаленный сервер в облаке
```
ssh <имя пользователя на сервере>@<IP-адрес сервера>
```
- Остановите службу nginx
```
sudo systemctl stop nginx
```
- Установите docker:
```
sudo apt install docker.io
```
- Установите docker-compose
- Скопируйте файлы docker-compose.yml и nginx/default.conf из вашего проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно:
```
scp ./docker-compose.yml <имя пользователя на сервере>@<IP-адрес сервера>:~/
scp ./nginx.conf <имя пользователя на сервере>@<IP-адрес сервера>:~/
```
- Программные инструкции по развертыванию контейнеров описаны в файле docker-compose.yml
- Workflow для GitHub Actions описано в файле yamdb_workflow.yml

После успешного прохождения workflow на GitHub Actions необходимо выполнить следующие команды на сервере.

- Подготовить миграции для базы данных:
```
sudo docker-compose exec backend python manage.py makemigrations
```
- Выполнить миграции:
```
sudo docker-compose exec backend python manage.py migrate
```
- Создать суперюзера для проекта:
```
sudo docker-compose exec backend python manage.py createsuperuser
```
- Собрать статические файлы в отдельную папку:
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
- Наполнить базу данных ингредиентами для создания рецептов можно командой:
```
sudo docker-compose exec backend python manage.py load_csv_file
```

### Шаблон наполнения env-файла
```
SECRET_KEY = '...' # секретный ключ
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=... # логин для подключения к базе данных
POSTGRES_PASSWORD=... # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=.... # порт для подключения к БД
```

### Автор/Author 
Михаил Федоров / Mikhail Fedorov
