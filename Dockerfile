FROM python:latest

RUN useradd -m -u 1000 user

USER user

ENV  HOME=/home/user \
     PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY requirements.txt $HOME/app

RUN pip install --no-cache-dir --upgrade -r $HOME/app/requirements.txt

COPY . $HOME/app

EXPOSE 8000

CMD ["fastapi","run","main.py","--port","8000"]
