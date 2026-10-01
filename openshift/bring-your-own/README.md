# Bring Your Own

This scenario is designed for users who want to use their own infrastructure components. It showcases how users can
integrate their own signer keys and certificates, and connect to a separately deployed database through the v1 Securesign API.

## Prerequisites

- Ensure you are logged in to an OpenShift cluster.

## How to Deploy

To deploy this scenario, use the following command:

```sh
make deploy-all
```

This will execute the necessary steps to set up the environment with generated sample keys and a separate MariaDB database.
