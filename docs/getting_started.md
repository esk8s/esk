# Getting started

In this guide, we'll:
- create a `SecretPolicy` resource to enable the creation of ExternalSecrets in a specific backend path
- create an `ExternalSecret` resource to generate a new secret in the backend
- create a `SecretBinding` resource to provision access for a service account to the secrets

The example resources used in this guide and additional ones are available [here](/docs/examples/resources).


## Step by step

Create a secret policy that allows management of secrets in `kv/.+` for vault backends and `kv2/.+` for all backends:

```
kubectl apply -f - <<EOF
apiVersion: esk.io/v1alpha1
kind: SecretPolicy
metadata:
  name: esk-example
  namespace: default
allow:
  - pattern: kv/.+
    backends:
      - vault
  - pattern: kv2/.+
EOF
```

Create the secret in a backend using an ExternalSecret (the values inserted here are supposed to be placeholders, not the actual values, read more [here](/docs/reference/secrets.md)):

```
kubectl apply -f - <<EOF
apiVersion: esk.io/v1alpha1
kind: ExternalSecret
metadata:
  name: esk-vault-example
  namespace: test
spec:
  backend: vault
  values:
    pass: gen
EOF
```

Create the binding to provision access for the `default` service account to the `esk-example-secret` secret:

```
kubectl apply -f - <<EOF
apiVersion: esk.io/v1alpha1
kind: SecretBinding
metadata:
  name: esk-example-bind
  namespace: default
spec:
  serviceAccount: default
  secrets:
    - name: esk-vault-example
EOF
```

Create a pod that accesses the secrets via the bind:

```
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: esk-example-app
  namespace: default
  annotations:
    secrets.esk.io/inject-bindings: "esk-example-bind"
spec:
  containers:
    - name: test
      image: busybox
      command:
        - cat
      args:
        - /esk/secrets/esk-example-bind
EOF
```

The webhook will deal with expanding this annotation and injecting an init container into the pod. The init container will contact the injector to retrieve the secrets and render the file template accordingly.
