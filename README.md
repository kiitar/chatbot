# BananaAI
Banana A.I. Project

1. install pipenv
- pip3 install pipenv

2. install packages
- pipenv install

3. enable pipenv shell
- pipenv shell

4. install postgres database

5. export database url to DATABASE_URL environment variable
- export DATABASE_URL=postgres://username:password@database_host:5432/database_name
- please add the line to ~/.bash_profile

6. generate yoyo config file
- python3 init_config.py

7. make sure configuration in yoyo.ini file is correct

8. apply database migration
- yoyo apply

9. load initial data
- python3 load_initial_data.py

10. run server
- python3 server.py --port 8000
# chatbot
