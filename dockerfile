FROM python
COPY app.py /app.py
COPY requirements.txt /requirements.txt
RUN pip install pip update
RUN pip install -r requirements.txt
ENV ACCESS_TOKEN=***********************
ENV API_KEY=****************
ENV HOST="****************" 
ENV PASSWORD="*******************" 
ENV REDISPORT=****
ENTRYPOINT python /app.py