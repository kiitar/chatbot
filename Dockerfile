FROM python:3.6

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CMD [ "python", "init_config.py" ]

# CMD [ "yoyo", "apply"]

# CMD [ "python", "load_initial_data.py" ]

# CMD [ "python", "server.py" ]