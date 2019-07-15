test:
	poetry run pytest --disable-warnings

run:
	cd traders && poetry run flask run

run80:
	cd traders && sudo poetry run flask run --port=80

babel:
	npx babel --watch traders/staticx --out-dir traders/static --presets react-app/prod

gen_secret:
	poetry run python -c 'import os; print(f"SECRET_KEY = {os.urandom(16)}")' > traders/secret.py