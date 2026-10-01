# v1alpha1 API Scenario

This example deploys Trusted Artifact Signer using the deprecated `rhtas.redhat.com/v1alpha1` Securesign API. The operator generates signer keys, provisions the Trillian database and storage, and exposes the services through OpenShift Routes. The existing in-cluster Cosign CronJobs exercise image signing and verification.

Use this example to exercise the v1alpha1 API. The [Simple](../simple/README.md) example uses the v1 API.

## Prerequisites

- An OpenShift cluster with a RHTAS operator that serves `rhtas.redhat.com/v1alpha1`.
- `kubectl`, `kustomize`, `envsubst`, and `make`.

## How to Deploy

```sh
make deploy-all
```

This installs the example Keycloak instance and deploys TAS in the `rhtas-v1alpha1` namespace. Generated manifests are written to `target/`; `make clean` removes them.
