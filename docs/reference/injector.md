# Injector

## Annotations

The following is a list of annotations processed by the mutating admission webhook present in the injector. You can control the behavior of the pod when accessing and rendering secrets by using the annotations.

```
secrets.esk.io/inject-bindings: CSV list of bindings to inject into the pod
secrets.esk.io/inject-template-bind-name: Override the template for a bind. Replace "bind-name" with the name of the bind to override
secrets.esk.io/inject-target-bind-name: Override the target for a bind. Replace "bind-name" with the name of the bind to override
secrets.esk.io/injected: Skip mutating the pod
```

If you want to override information for multiple binds, you can do the following:
```
secrets.esk.io/inject-bindings: 'bind1,bind2'
secrets.esk.io/inject-template-bind1: |
  password = {{ secret1.password }}
  user = {{ secret1.user }}
secrets.esk.io/inject-target-bind2: /tmp/temp-credentials.txt
```