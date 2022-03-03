# bra-database

Easily parse BRA (french risks of avalanche news) and create a structured database from PDFs

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

On Travis, use [encryption variables](https://docs.travis-ci.com/user/environment-variables/#defining-encrypted-variables-in-travisyml).

### Folder

```bash
    export BRA_PDF_FOLDER=$PWD/out
    export BRA_LOG_FOLDER=$PWD/logs
```
