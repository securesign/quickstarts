# Custom Ingress Configuration

This scenario demonstrates how to set up custom ingress for TAS services by turning off `externalAccess` on RHTAS CRDs.
This prevents the automatic creation of Routes/Ingress. After disabling, you can manually create and manage your own
Route/Ingress with the specific configurations you require, like TLS settings, hostnames, and annotations.

Examples of Routes can be found in the `routes/` directory for Fulcio, Rekor, Search UI, TimestampAuthority and TUF.

## Prerequisites

- Ensure you are logged in to an OpenShift cluster.

## How to Deploy

To deploy this scenario, use the following command:

```sh
make deploy-all
```

This will execute the necessary steps to set up the environment with automatically managed keys and database configurations.
