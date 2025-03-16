# llm-experimentation

Build the artifact registry & docker images
STEP1: Create artifact registry 
REPOSITORY_NAME=ollamacloudrundemo

STEP2: 
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=docker \
    --location=us-central1 \
    --description="My Docker repository"

STEP3: Authorize
gcloud auth configure-docker us-central1-docker.pkg.dev


STEP3: edit the docker file

STEP4: 
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/ollama-deepseek \
  --machine-type e2-highcpu-32

