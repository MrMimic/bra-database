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

### Date

By default, the program will use the current date. You can change it by setting the `BRA_DATE` environment variable.

```bash
    export BRA_DATE=20220304
```

### Folder

Once dockerised, paths are ensured. Locally, run:

```bash
    mkdir $PWD/out $PWD/logs
    export BRA_PDF_FOLDER=$PWD/out/$BRA_DATE
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

You can also specify the date to use with:

```bash
    docker run --env BRA_DATE=$BRA_DATE bra/backend:latest
```
