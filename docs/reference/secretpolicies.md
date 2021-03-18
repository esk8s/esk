
# Secret policies

Policies control the creation and update of secrets via regex patterns. Patterns can be defined for both allowing and rejecting secret paths.
Currently only secrets paths are checked.

```
allow:
  - pattern: ""
    backends:
      - vault
      - aws
      - gcp
reject:
  - pattern: ""
```

Each rule supports the following parameters:
- pattern: "" # required. regex pattern to match the secret path with
- backends: [] # optional. backends this pattern applies to


## Parameters

The following is a list of all possible parameters for a policy. 


### Allow

Which paths are allowed to be accessed in the specified (or all) backends.


### Reject

Which paths are <b>not</b> allowed to be accessed in the specified (or all) backends.