# Secrets

Example spec:

```
spec:
  values: {}
  backend: ""
  path: ""
  placeholder: bool
  maxVersions: 0
  recoveryDays: 0
  replication: ""
```

## Parameters

The following is a list of all possible parameters for a secret. 


### Backend (required)

Controls which backend hosts this secret


### Values (required)

Dict of values that are to be generated/persisted in the backend. Possible values that are processed are:
- gen: generate a random string of length 32
- gen(\d+): generate a random string with the provided length


### Path

Path in the backend system where the secret is located. Defaults to `<namespace>-<name>`


### Placeholder

Whether the resource is just a placeholder to prevent overwriting the path with other values. This is set to true when the secret being handled is not supposed to be generated but instead requires manual intervention. An example is a API key that is generated outside ESK.

Defaults to false.


### MaxVersions (Vault only)

Max number of versions for a secret.


### RecoveryDays (AWS only)

Number of days the secret will stay marked for deletion before really being deleted.


### Replication (GCP only)

Replication strategy for the secret
