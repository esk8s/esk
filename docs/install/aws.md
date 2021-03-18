
# AWS backend configuration

Coming soon!

## Chart values

Adapt the chart values as follows:

```
operator:
  serviceAccount:
    create: true
    annotations:
      eks.amazonaws.com/role-arn: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${OPERATOR_SA_NAME}

injector:
  serviceAccount:
    create: true
    annotations:
      eks.amazonaws.com/role-arn: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${INJECTOR_SA_NAME}

backends:
  aws:
    enabled: true
```
