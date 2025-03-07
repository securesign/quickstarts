# Simple Scenario

This scenario provides an easy and quick setup of TAS (Trusted Artifact Signer). All required prerequisites are
managed by the operator and automatically generated if they are required. It will generate all signer keys,
provision a MariaDB database for Trillian, and create persistence claims with the default persistence volume driver.

## Prerequisites

- Ensure you are logged in to an OpenShift cluster.

## How to Deploy

To deploy this scenario, use the following command:

```sh
make deploy-all
```

This will execute the necessary steps to set up the environment with automatically managed keys and database configurations.
