# Gateway API
This example demonstrates how to secure Red Hat Trusted Artifact Signer (RHTAS) services using Kubernetes Gateway API
and Kuadrant. It shows how to enforce authentication, authorization and rate limiting on RHTAS endpoints via
Kubernetes Service Account tokens and ClusterRoles. The scenario includes:
- Authentication via Authorization: Bearer $TOKEN headers
- Role-based access control with `rhtas-reader` and `rhtas-writer` ClusterRoles
- Rate limiting via Kuadrant policies
- A workaround for the cosign CLI's lack of authentication support using `mitmproxy`

## Prerequisites

- Ensure you are logged in to an OpenShift cluster.
- [mitmproxy](https://mitmproxy.org/)

## How to Deploy

To deploy this scenario, use the following command:

```sh
make deploy-all
```

## Scenarios

Set environment variables
```sh
export TUF_URL=https://$(oc get route tuf -n rhtas-gateway-api -o jsonpath='{.spec.host}')
export REKOR_URL=https://$(oc get route rekor -n rhtas-gateway-api -o jsonpath='{.spec.host}')
export FULCIO_URL=https://$(oc get route fulcio -n rhtas-gateway-api -o jsonpath='{.spec.host}')
```

### Access the API Without Authentication
```sh
curl $FULCIO_URL/api/v2/trustBundle -i
# HTTP/1.1 401 Unauthorized
# www-authenticate: Bearer realm="k8s-service-accounts"
# x-ext-auth-reason: credential not found
```

### Access the API With Authentication But Without Sufficient Permissions

Obtain an access token for the client-app-3 service account:
```sh
TOKEN=$(kubectl create token -n default client-app-3)
```

Send a request to the API as the service account while still missing permissions:
```sh
curl -H "Authorization: Bearer $TOKEN" $FULCIO_URL/api/v2/trustBundle -i
# HTTP/1.1 403 Forbidden
```

### Access the API With Read Permission

Obtain an access token for the client-app-2 service account:
```sh
TOKEN=$(kubectl create token -n default client-app-2)
```

Send requests to the API as the Kubernetes service account:
```sh
curl -H "Authorization: Bearer $TOKEN" $FULCIO_URL/api/v2/trustBundle -i
# HTTP/1.1 200 OK
```

Send write request (without permission):
```sh
curl -H "Authorization: Bearer $TOKEN" -X POST $FULCIO_URL/api/v2/signingCert -i
# HTTP/1.1 403 Forbidden
```

### Try the API rate limited
Each service account is subject to a rate limiting policy defined by Kuadrant. The default configuration enforces a
limit of 5 requests every 10 seconds per service account identity. When the rate limit is exceeded, the API will return
a 429 Too Many Requests response. This behavior helps to prevent abuse or accidental overload of the RHTAS services.

You can test rate limiting using the following loop:
```sh
while :; do curl --write-out '%{http_code}\n' --silent --output /dev/null -H "Authorization: Bearer $TOKEN" $FULCIO_URL/api/v2/trustBundle | grep -E --color "\b(429)\b|$"; sleep 1; done
```

This loop continuously sends requests and highlights when the rate limit is hit.

The rate limit policy is configured using Kuadrant's RateLimitPolicy custom resource, which can be tuned to apply
different limits based on service account identity, HTTP paths, or request methods.

### Try to sign container image

Prerequisites:
 - [mitmproxy](https://mitmproxy.org/) must be installed and accessible.
 - setup mitmproxy CA certificate https://docs.mitmproxy.org/stable/concepts-certificates/

Obtain an access token for the client-app-1 service account:
```sh
TOKEN=$(kubectl create token -n default client-app-1)
```

Launch mitmproxy to inject the Authorization header:
```sh
TOKEN=$TOKEN mitmdump --mode regular --listen-port 9090 -s ./proxy/inject_auth.py
```

Build and Push a container image
```sh
#build image
export IMAGE_NAME=ttl.sh/rhtas/example:5min
echo "from scratch" | podman build -f - -t $IMAGE_NAME
podman push $IMAGE_NAME
```

Sign the image using cosign
```sh
#initialize
HTTP_PROXY=127.0.0.1:9090 HTTPS_PROXY=127.0.0.1:9090 NO_PROXY=oauth2.sigstore.dev,ttl.sh cosign initialize --mirror=$TUF_URL --root=$TUF_URL/root.json

#sign image
HTTP_PROXY=127.0.0.1:9090 HTTPS_PROXY=127.0.0.1:9090 NO_PROXY=oauth2.sigstore.dev,ttl.sh cosign sign --fulcio-url=$FULCIO_URL --rekor-url=$REKOR_URL --oidc-issuer="https://oauth2.sigstore.dev/auth" -y $IMAGE_NAME
```

