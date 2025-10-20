FROM python:3.9-slim    

RUN apt-get update && apt-get install -y curl

RUN useradd --create-home --shell /bin/bash app

WORKDIR /home/app

COPY app/requirements.txt  .
RUN pip install --no-cache-dir -r requirements.txt 

COPY app/ .

# Set permissions
RUN chown -R app:app /home/app && chmod +x start.sh

USER app

EXPOSE 5000

CMD ["./start.sh"]

