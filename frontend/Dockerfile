FROM nginx:alpine

# Copy frontend files
COPY . /usr/share/nginx/html
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

COPY ./config.template.js /usr/share/nginx/html/config.js
COPY ./start.sh /start.sh
RUN chmod +x /start.sh
EXPOSE 80

CMD ["./start.sh"]
