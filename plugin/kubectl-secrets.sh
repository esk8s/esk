#!/bin/sh

# VERSION: 1.0.0

while [ $# -gt 0 ]; do
  case ${1} in
      -n)
          namespace="$2"
          shift
          ;;
      "read")
          ;;
      *)
          secret="$1"
          ;;
  esac
  shift
done

if [ -z "$namespace" ]; then namespace=`kubectl config view --minify | grep namespace | cut -d " " -f 2`; fi

token=`kubectl config view --minify --raw | grep token | cut -d ":" -f 2 | xargs`

if [ -z "$token" ];
then
  password=`kubectl config view --minify --raw | grep "password:" | cut -d ":" -f 2 | xargs`
  user=`kubectl config view --minify --raw | grep "username:" | cut -d ":" -f 2 | xargs`

  token=`printf "$user:$password" | base64`
fi

echo '{
  "auth": "Basic '$token'",
  "name": "'$secret'",
  "namespace": "'$namespace'"
}' | kubectl create --raw "/api/v1/namespaces/secretsplane/services/https:esk-injector:443/proxy/readsecret" -f -