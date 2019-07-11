test:
	poetry run pytest --disable-warnings

run:
	cd traders && poetry run flask run