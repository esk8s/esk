
# Vault backend configuration

Authentication and authorization to Vault has to be configured for both the processor and the operator. Currently, only (kubernetes engine auth)[https://www.vaultproject.io/docs/auth/kubernetes] is supported.

## Export names

```
export INJECTOR_SA_NAME=esk-injector
export OPERATOR_SA_NAME=esk-operator
```

## Create Policies

Create the policies to provide for both service accounts in vault.

```
vault policy write esk-operator - <<EOF
path "kv/*" {
  capabilities = ["read","create","update","delete"]
}
EOF

vault policy write esk-injector - <<EOF
path "kv/data/*" {
  capabilities = ["read"]
}
EOF
```

## Roles

Create the kubernetes authentication roles for both service accounts.

```
vault write auth/kubernetes/role/esk-operator \
        bound_service_account_names=$OPERATOR_SA_NAME \
        bound_service_account_namespaces=esk \
        policies=esk-operator

vault write auth/kubernetes/role/esk-injector \
        bound_service_account_names=$INJECTOR_SA_NAME \
        bound_service_account_namespaces=esk \
        policies=esk-injector \
        ttl=24h
```

## Chart values

Adapt the chart values as follows:

```
operator:
  podAnnotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: esk-operator
    vault.hashicorp.com/agent-inject-token: "true"

injector:
  podAnnotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: esk-injector
    vault.hashicorp.com/agent-inject-token: "true"

backends:
  vault:
    enabled: true
    address: https://vault.example.com
    token_path: /vault/secrets/token
    defaultMountPoint: kv
```