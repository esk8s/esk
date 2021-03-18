
# Secret bindings

Secret bindings serve two purposes:
- tie service accounts to secrets (via kubernetes roles and rolebindings)
- provide the mutating webhook information to inject into the init container, listing which secrets to fetch and how to render them (via special annotations)

They are not strictly required to be used, since both purposes can be achieved in another way, but they bring bigger flexibility.

Gotchas:
- A pod can use more than one secret binding at a time.
- A bind can only be rendered once per pod

```
spec:
  serviceAccount: ""
  secrets: [
    { name }
  ]
  template: ""
  target: ""
```


## Parameters

The following is a list of all possible parameters for a policy. 


### Service Account (required)

The service account that is granted access to the listed secrets


### Secrets (required)

The list of secrets the service account will access


### Template (optional)

Define how to render the secrets in the pod. A secret value is templated into a string such as "{{ [secret name].[key] }}".

Defaults to:
```
[secret1].[key1] = {{ [secret1].[key1] }}
[secret2].[key3] = {{ [secret2].[key3] }}
```


### Target (optional)

Path in the pod where to render the template to. Defaults to /esk/secrets/<bind name>