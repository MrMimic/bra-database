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
    mkdir $PWD/out $PWD/logs $PWD/img
    export BRA_PDF_FOLDER=$PWD/out/$BRA_DATE
    export BRA_LOG_FOLDER=$PWD/logs
    export BRA_IMG_FOLDER=$PWD/img
```

### Docker

Build locally:

```bash
    docker build -t bra/backend:latest .
```

To build it on GCP:

```bash
    gcloud builds submit --tag gcr.io/data-baguette/bra-database
```

## Run locally

Run every day the following command:

```bash
    docker run bra/backend:latest
```

You can also specify the date to use with:

```bash
    docker run --env BRA_DATE=$BRA_DATE bra/backend:latest
```

## Scheduling

Create a GKE cluster:

```bash
    gcloud container clusters create-auto bra --region REGION --project=PROJECT
```

Create a NAT router:

```bash
gcloud compute routers create bra-nat-router \
    --network default \
    --region REGION \
    --project=PROJECT
```

Add an external mapping configuration (to get traffic outside the cluster):

```bash
gcloud compute routers nats create bra-nat-router-config \
    --region REGION \
    --router bra-nat-router \
    --nat-all-subnet-ip-ranges \
    --auto-allocate-nat-external-ips \
    --project=PROJECT
```

Log kubectl to the GKE:

```bash
gcloud container clusters get-credentials bra \
    --region REGION \
    --project=PROJECT
kubectl get all --all-namespaces
```

Upload a secret yaml file on GKE containing the DB connection informations:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  MYSQL_USER: 
  MYSQL_PWD: 
  MYSQL_HOST: 
  MYSQL_PORT: 
  MYSQL_DB: 
  MYSQL_TABLE: 
```

> Note: values should be base64 encoded with `echo -n "MY_VALUE" | base64`.

```bash
    kubectl apply -f secret.yaml
```

And apply the cron job to the GKE:

```bash
kubectl apply -f $PWD/cronjob.yaml
```

### Debug

#### Bug 1

```sql
    SELECT `date`, massif, until, departs, declanchements, risk_score, risk_str, stabilite_manteau_bloc, situation_avalancheuse_typique, departs_spontanes, declanchements_provoques, qualite_neige
    FROM bra.france
    WHERE departs_spontanes IS NULL
    ORDER BY `date` DESC;
```

Some massifs never return the keys from the snow quality because these BRA does not use the same format than others for the keys.

```json
    {
        "declenchements accidentels": "de rares plaques peuvent encore persister en versant nord d'altitude peux fr??quent??s en effet, par endroit la vielle poudreuse qui ?? ??volu?? en faces planes sans coh??sion est recouverte par de la neige plus ou moins fritt??e ce qui forme alors une plaque la surface du manteau ??tant tr??s h??t??rog??ne en ce moment, ces rares plaques sont plut??t de petites surfaces et ne se semblent, de plus, ne pas vouloir se d??clencher facilement d'apr??s les derniers tests de stabilit?? effectu??s cela reste toutefois possible localement y compris par un seul skieur dans les secteurs peu ou pas trac??s",
        "departs naturels": "peu probable avec un air sec et froid qui persiste encore, m??me si une ou deux plaques de fond ont pu ??tre signal??es ces derniers temps une corniche peut c??der (tr??s rarement, mais observ??) et d??clencher une plaque en contre bas"
    }
```
