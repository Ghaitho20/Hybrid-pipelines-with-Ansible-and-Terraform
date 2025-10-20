#!/bin/sh
envsubst '$API_URL' < /usr/share/nginx/html/config.template.js > /usr/share/nginx/html/config.js
nginx -g 'daemon off;'
