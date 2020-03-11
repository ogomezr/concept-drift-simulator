FROM python:3.7.2-slim

WORKDIR /home/knives/concept-drift-simulator

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050

CMD gunicorn -b 0.0.0.0:8050 app:server 
