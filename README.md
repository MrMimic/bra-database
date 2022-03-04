# bra-database

Easily parse BRA (french risks of avalanche news) and create a structured database from PDFs.

## Setup

### Database

Locally, create a .env file containing:

```bash
    MYSQL_USER=
    MYSQL_PWD=
    MYSQL_HOST=
    MYSQL_PORT=
    MYSQL_DB=
    MYSQL_TABLE=
```

### Folder

Once dockerised, paths are ensured. Locally, run:

```bash
    mkdir $PWD/out $PWD/logs
    export BRA_PDF_FOLDER=$PWD/out
    export BRA_LOG_FOLDER=$PWD/logs
```

### Docker

Build locally:

```bash
    docker build -t bra/backend:latest .
```

## Run

Run every day the following command:

```bash
    docker run bra/backend:latest
```
