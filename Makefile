pull:
	git checkout main && git pull
run:
	python manage.py runserver 8005
gun:
	gunicorn mysite.wsgi:application --reload -c gunicorn.conf.py
migrate:
	python manage.py makemigrations && python manage.py migrate
activate:
	source env/bin/activate
test:
	export DJANGO_SETTINGS_MODULE=mysite.settings && pytest -vv
cm:
	git add . && git commit -m 'updates'
push:
	git push
install:
	pip install -r requirements.txt
deploy:
	sudo systemctl restart invoisce && sudo systemctl restart nginx
deploy0:
	export DJANGO_SETTINGS_MODULE=mysite.settings.prod && sudo systemctl restart invoisce && sudo systemctl restart nginx
