# Kubectl plugin

## Install

```
curl -Lo https://raw.githubusercontent.com/tiagoposse/esk/master/plugin/kubectl-secrets.sh
chmod +x kubectl-secrets.sh
mv kubectl-secrets.sh /usr/local/bin
```

## Uninstall

```
rm /usr/local/bin/kubectl-secrets.sh
```

## Usage

```
kubectl secrets read [name] -n [namespace]
```