# Deploying Dex on OpenShift
This section provides instructions for deploying the Dex Identity Provider on an OpenShift cluster using the provided manifests and Makefile.

Before you begin, ensure you have the following:

- OpenShift Cluster Access: You must have access to an OpenShift cluster.
- oc CLI Tool: The OpenShift command-line interface (oc) must be installed on your local machine.
- Logged In: You must be logged into your OpenShift cluster via oc login and have the necessary permissions to create namespaces, deployments, services, routes, and configmaps.

## Step 1: Prepare Your Dex Configuration Template
Open dex-config.yaml.template in your text editor.
Crucially, review and customize the staticClients and staticPasswords sections.
The defaults are `jdoe@redhat.com` with the password `secure`. create your own ones if you want, I commented a command on how to get the hashed password.
The default client ID is 'trusted-artifact-signer' and client secret 'ZXhhbXBsZS1hcHAtc2VjcmV0'

## Step 2: Deploy Dex
Open your terminal

Ensure you are logged into your target OpenShift cluster using oc login.

Run the deploy command:

```Bash
make deploy
```

This command will:

Automatically detect your OpenShift cluster's application domain.
Generate the final dex-config.yaml from the template, injecting the correct domain.
Create the dex-idp namespace.
Deploy the Dex Deployment, Service, and Route into the dex-idp namespace.
Wait for the Dex pod to be ready.
Finally, print the external URL you can use to access the Dex Identity Provider.

## Step 3: Access Dex
Once the make deploy command completes, it will output the Access URL for your Dex instance. It will look something like this:

Access URL: https://dex-idp-route-dex-idp.apps.your-cluster-domain.com/dex

This is the URL that will go into your Fulcio OIDC configuration and be the OIDC issuer url that you will use to sign and verify.
`--oauth-force-oob` or equivalent is recommended for signing if using externally outside the cluster as the default oauth2 flow redirects to localhost which is not configured if used outside of the cluster domain. (You can add it yourself, otherwise OOB oauth2 works just fine)

## Step 4: Clean Up (Optional)
To remove all deployed Dex resources from your cluster:

```Bash
make clean
```

This will delete the Deployment, Service, Route, and ConfigMap associated with Dex in the dex-idp namespace.

## Notes
This deployment uses a mock/static Dex connector and is not intended for production use.

Designed for use in TAS development and testing workflows.
