
External Secrets for Kubernetes is an open source project that provides a way to manage external secrets as kubernetes resources.
Secrets are never really stored in kubernetes, but instead stored in the secret management system and access to them regulated via Roles and Rolebindings.
Currently, [Hashicorp Vault](https://www.vaultproject.io), [Google SecretManager](https://cloud.google.com/secret-manager/) and [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) are supported.

The tool exposes three types of resources:
- `ExternalSecret`: exposes secret definitions on how they're to be generated in the backend
- `SecretBinding`: grants a kubernetes service account access to a list of secrets
- `SecretPolicy`: controls the paths that can be managed in backends for each namespace

For a quick guide on creating your first secret, read below. For more information, read the reference [here](/docs/reference/).

The main use case is to create a secret such as:
```
apiVersion: esk.io/v1alpha1
kind: ExternalSecret
metadata:
  name: esk-gcp-example
  namespace: default
spec:
  backend: gcp
  values:
    gcp: test
    pass: gen
```

Gets stored in GCP with the following values:
```
{
  "gcp": "test"
  "pass": "a.WcpnUS$5J@qVyU|\GzbeqtTLWaiN@e"
}
```


# Releases

| Release | Release Date |
| ---     |     ---      |
| v0.6.0  | 17/03/2021   |


# Getting started

## Prerequisites

Depending on which backends you want to use in ESK, you need to configure access for the service accounts used by the operator and the injector. Please follow the following link to configure your intended secrets backend:
- [Vault](/docs/install/vault.md)
- [GCP](/docs/install/gcp.md)
- [AWS](/docs/install/aws.md)


## Install via helm

```
helm repo add esk https://esk8s.github.io/esk-chart
helm install esk/esk
```

Code for the chart is [here](https://github.com/esk8s/esk-chart).


## Creating your first secret

Please follow the guide [here](/docs/getting_started.md) to go through creating and accessing a secret.


# Read secrets from cli

You can read the secret values for an ExternalSecret resource by using the kubectl plugin from this repo. Installation instructions [here](/docs/plugin.md)

# Overview

ESK is composed of 2 main components:
- An operator responsible for managing the secrets in the backends
- A webhook/webserver responsible for mutating pods to inject an init container and for answering secret read requests

The architecture looks as follows:

<kbd>
<img src="/docs/arch/images/arch.png" width="400" />
</kbd>

More architectural diagrams are available [here](/docs/arch).