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
    mkdir $PWD/out $PWD/logs $PWD/IMG
    export BRA_PDF_FOLDER=$PWD/out/$BRA_DATE
    export BRA_LOG_FOLDER=$PWD/logs
    export BRA_IMG_FOLDER=$PWD/IMG
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

### Debug

```sql
    SELECT `date`, massif, until, departs, declanchements, risk_score, risk_str, stabilite_manteau_bloc, situation_avalancheuse_typique, departs_spontanes, declanchements_provoques, qualite_neige
    FROM bra.france
    WHERE departs_spontanes IS NULL
    ORDER BY `date` DESC;
```

Some massifs never return the keys from the snow quality because these BRA does not use the same format than others for the keys.

```json
    {
        "declenchements accidentels": "de rares plaques peuvent encore persister en versant nord d'altitude peux fréquentés en effet, par endroit la vielle poudreuse qui à évolué en faces planes sans cohésion est recouverte par de la neige plus ou moins frittée ce qui forme alors une plaque la surface du manteau étant très hétérogène en ce moment, ces rares plaques sont plutôt de petites surfaces et ne se semblent, de plus, ne pas vouloir se déclencher facilement d'après les derniers tests de stabilité effectués cela reste toutefois possible localement y compris par un seul skieur dans les secteurs peu ou pas tracés",
        "departs naturels": "peu probable avec un air sec et froid qui persiste encore, même si une ou deux plaques de fond ont pu être signalées ces derniers temps une corniche peut céder (très rarement, mais observé) et déclencher une plaque en contre bas"
    }
```
