# llm-experimentation

Build the artifact registry & docker images

STEP1: Set Variables
REPOSITORY_NAME=ollamacloudrundemo
PROJECT_ID=*project_id*

STEP2: Create artifact registry 
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=docker \
    --location=us-central1 \
    --description="My Docker repository"


STEP3: Authorize user credentials to access the artifact registry
gcloud auth configure-docker us-central1-docker.pkg.dev


STEP4: Create a director for the ollama container
mkdir ollama
cd ollama

STEP4: Create Docker file
touch Dockerfile
copy from Dockerfile

Step 5: Trigger the google cloud build to create the container image
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/ollama-deepseek \
  --machine-type e2-highcpu-32

Step 6: Build Open webui containter (no need to create a docker file you can pull it as is)
cd ..
mkdir openwebui
docker pull ghcr.io/open-webui/open-webui:main

Step 7: Tag the docker image and then publish it
docker tag ghcr.io/open-webui/open-webui:main us-central1-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/openwebui
docker push us-central1-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/openwebui

*now the build is completed for both the ollama-deepseek and openwebui* - completes first part 

Second Part = leveraging the google cloud run to setup the service for each

ollama-deepseek:
leverage the GPU + Container Port = 11434 (standard ollama port)
Resources 16gb and 4 CPUs
instance based billing

to test if instance is up and run leverage the below code: 
curl https://ollama-deepseek-864831823457.us-central1.run.app/api/generate -d '{ 
 "model": "deepseek-r1:7b" 
 "prompt": "Why is the sky blue?" 
}'


openwebui: 
Resources 16gb and 4 CPUs
add a variable [OLLAMA_BASE_URL = *url for ollama model*]
request based billing is fine

---

# Hong Kong Marketing Intelligence Pipeline

PostgreSQL + pgvector database with baseline ingestion, active enrichment, and AEO embedding generation.

## Setup
```bash
cp .env.example .env        # set OPENAI_API_KEY; DB_URL defaults to local compose DB
docker compose up -d postgres redis   # schema.sql is applied automatically on first boot
pip install -r requirements.txt
# apply schema manually to an existing DB:
psql "$DB_URL" -f schema.sql
```

## Run
```bash
./scripts/run_baseline_ingest.sh data/storeleads.csv      # csv / json / jsonl; upserts companies (country HK)
./scripts/run_enrichment_worker.sh                        # enriches companies not updated in 30 days (EMBED=1 also embeds)
PYTHONPATH=. python -m src.enrichment.generate_aeo_embeddings   # text-embedding-3-small -> aeo_audits.embeddings
docker compose up -d worker                               # run the enrichment loop as a service
```
Tests: `PYTHONPATH=. pytest tests`.

Layout: `schema.sql` (schema + HNSW vector index), `src/db` (pooled client), `src/ingestion`, `src/enrichment`, `src/utils`, `scripts/`.
