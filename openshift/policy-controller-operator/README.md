# Policy Controller Operator

This quickstart deploys the Policy Controller Operator on OpenShift. The Policy Controller enforces image signing
policies using Sigstore, allowing you to define and enforce policies that require container images to be signed
before they can be deployed.

## Prerequisites

- Ensure you are logged in to an OpenShift cluster.
- The RHTAS (SecureSign) operator must be installed on the cluster.
- The `oc` CLI tool.

## How to Deploy

Set the required environment variables, then run the deploy command:

```sh
export RHTAS_INSTALL_NAMESPACE=<rhtas-install-namespace>
export OIDC_ISSUER_URL=<your-oidc-issuer>
export OIDC_SUBJECT=<your-oidc-subject>

make deploy-all
```

The `FULCIO_URL`, `REKOR_URL`, `TUF_URL`, and `BASE64_TUF_ROOT` values are automatically retrieved from the RHTAS installation. You can override them by setting them as environment variables before running the command.

This will:

1. Install the Policy Controller Operator via OLM subscription.
2. Wait for the operator CSV to succeed.
3. Deploy the PolicyController custom resource with webhook configuration.
4. Wait for the policy controller deployments to be ready.
5. Deploy the TrustRoot and ClusterImagePolicy resources.

## Testing

Create a namespace with the `policy.rhtas.com/include: "true"` label:

```sh
oc create namespace policy-controller-test-ns
oc label namespace policy-controller-test-ns policy.rhtas.com/include=true
```

Try to create a pod in the namespace, it should be rejected because the image is not signed:

```sh
oc -n policy-controller-test-ns run test --image=quay.io/example/unsigned-image:latest
```

Sign the image with your RHTAS instance, then try again, the pod should be created successfully.

## Clean Up

To remove test ns:

```sh
oc delete ns policy-controller-test-ns
```

To remove all cluster resources:

```sh
make undeploy
```

To remove all local resources:

```sh
make clean
```
