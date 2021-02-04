FROM python:3.8.5

WORKDIR /usr/src/artway

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
#RUN apk update && apk add gcc libc-dev make git libffi-dev openssl-dev python3-dev libxml2-dev libxslt-dev
#RUN apk --update add libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev curl
#RUN apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
#RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
#RUN apk add --update nodejs nodejs-npm
#RUN apk add --update --no-cache g++ gcc libxslt-dev
#RUN apk add --update --no-cache --virtual .build-deps \
#        g++ \
#        libxml2 \
#        libxml2-dev && \
#    apk add libxslt-dev

#RUN apt-get update && apt-get upgrade -y && \
#    apt-get install -y nodejs \
#    npm

#RUN apt-get install nodejs npm


#WORKDIR /usr/src/artway/frontend
#RUN npm install
#RUN npm run-script build

COPY . .
WORKDIR /usr/src/artway
RUN pip install -r requirements.txt
RUN python3 manage.py collectstatic --noinput