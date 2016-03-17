USER=root
PASSWORD=12345678
CREATE_DATABASE=configs/mysql/create.sql
DROP_DATABASE=configs/mysql/clear.sql

all: data

data:
	python manage.py structured

update_db: sql
	python manage.py migrate

init_db: create_database sql
	python manage.py migrate

drop_db: drop_database

sql:
	python manage.py makemigrations clawer_parse

drop_database:
	mysql -u$(USER) -p$(PASSWORD) < $(DROP_DATABASE)

create_database:
	mysql -u$(USER) -p$(PASSWORD) < $(CREATE_DATABASE)
