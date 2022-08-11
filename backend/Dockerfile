FROM python:3.9.10-slim as backend

COPY ./utils.py ./main.py ./database.py ./model.py /app/
COPY ./requirements.txt /app
COPY ./data /app/data
ARG DB_URL="mongodb://davidn:ciscopsdt@10.0.0.60:27017/"
ARG VIRTUAL=0
ENV DB_CONNECT_URL=${DB_URL}
ENV VIRTUAL_EVENT=${VIRTUAL}

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0"]
