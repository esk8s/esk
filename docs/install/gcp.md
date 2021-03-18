
# GCP backend configuration

For this tutorial, (workload identity needs to be enabled in your cluster)[https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#kubectl].


## Export names

```
export INJECTOR_SA_NAME=esk-injector
export OPERATOR_SA_NAME=esk-operator
export PROJECT_ID=<< PROJ_ID>>
```

## Create the service accounts

Create google service accounts to bind to kubernetes service accounts

```
gcloud iam service-accounts create $OPERATOR_SA_NAME \
    --description="Service account used by the ESK Operator to manage secrets" \
    --display-name="esk-operator"

gcloud iam service-accounts create $INJECTOR_SA_NAME \
    --description="Service account used by the ESK Injector to read secrets" \
    --display-name="esk-injector"
```

## Grant project permissions

Grant the google service accounts the required permissions to access/manage secrets in secretmanager

```
gcloud projects add-iam-policy-binding --role="roles/secretmanager.admin" ${PROJECT_ID} --member "serviceAccount:${OPERATOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding --role="roles/secretmanager.secretAccessor" ${PROJECT_ID} --member "serviceAccount:${INJECTOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
```


## Grant workload permissions

Grant the kubernetes service accounts the required permissions to act as the google service accounts

```
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[esk/${OPERATOR_SA_NAME}]" \
  ${OPERATOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[esk/${INJECTOR_SA_NAME}]" \
  ${INJECTOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
```


## Chart values

Adapt the chart values as follows:

```
operator:
  serviceAccount:
    create: true
    annotations:
      iam.gke.io/gcp-service-account: ${OPERATOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

injector:
  serviceAccount:
    create: true
    annotations:
      iam.gke.io/gcp-service-account: ${INJECTOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

backends:
  gcp:
    enabled: true
    projectID: ${PROJECT_ID}
```