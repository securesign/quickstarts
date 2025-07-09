# OpenShift Cluster Pools on AWS (via Hive)

## Introduction to Hive Cluster Pools
This document provides an overview and instructions for utilizing OpenShift Cluster Pools on AWS, managed by Red Hat Hive. Cluster Pools allow us to quickly provision pre-initialized OpenShift clusters for development, testing, or specific use cases, significantly reducing the typical cluster deployment time.

Instead of waiting for a full OpenShift cluster to deploy from scratch (which can take 30-60+ minutes), Cluster Pools maintain a 'warm' set of Single Node OpenShift (SNO) clusters. When a cluster is "claimed," it's almost immediately ready for use, and the pool automatically initiates the deployment of a new replacement cluster in the background.

## Important Considerations for AWS Deployments

Our AWS accounts are configured with an automated resource management process known as dpp-pruner. This automated tool is designed to identify and delete unused or idle AWS resources (such as Elastic IPs, EC2 instances, etc.) to optimize costs and manage our cloud footprint.

If you anticipate needing a cluster for an extended period or observe unexpected deletion of resources related to your claimed cluster, you may need to request an exemption for specific resources from the dpp-pruner.

## Prerequisites

Before you begin, ensure you have the following:

### CLI Tools Setup:

oc or kubectl CLI: Configured and authenticated to your Hive management cluster.

AWS CLI: You need to create an rhtas profile on your AWS CLI. The necessary details for this profile are located in our Bitwarden vault under the "Hive EKS Cluster" entry. This profile will be used by the kubeconfig file to provision cluster pools.

Hive kubeconfig: Export the Hive kubeconfig file (also available in our Bitwarden vault) into your KUBECONFIG environment variable. This grants you access to the Hive cluster.

The default region for these operations is us-east-1.

AWS Account and Credentials: An AWS account with sufficient permissions to create OpenShift clusters (EC2, VPC, Route 53, IAM, S3, ELB). Our team's AWS account is already configured to work for this purpose. The AWS credentials for the hive-service user (found in Bitwarden) will be used by the Cluster Pool.

Public DNS Domain: A registered public DNS domain that you can manage (e.g., via AWS Route 53) and delegate to OpenShift for cluster API and Ingress. Our managed domain for this is rhtas.ccitredhat.com.

OpenShift Pull Secret: A valid pull secret from cloud.redhat.com is required to pull OpenShift release images. While typically included in the install-config.yaml template, ensure it is available if needed.

### Cluster Pool Configuration Details

To create a cluster pool, you will need to modify the clusterPool.yaml file located in this directory. You must update the parameters marked with CHANGEME placeholders.

SSH Key: The SSH key required for the cluster nodes is the "Hive SSH key" available in our Bitwarden vault.

AWS Credentials: The AWS credentials for the hive-service user, also found in Bitwarden, will be used by the Cluster Pool to interact with AWS.

Default Configuration: The provided clusterPool.yaml is pre-configured to:

Maintain one cluster in the pool, ready on standby to be claimed.

Install OpenShift Container Platform (OCP) version 4.15.

Utilize a t3a.xlarge EC2 instance type for the cluster node.

Replenishment: Once a cluster is claimed from the pool, Hive will automatically initiate the provisioning of another cluster to replenish the empty slot, ensuring the pool maintains its configured size.

## Steps to Create a Cluster Pool

Apply the cluster pool configuration as such:

`oc apply -f clusterPool.yaml`

### Monitoring the Cluster Pool Deployment

After applying the ClusterPool, Hive will begin provisioning clusters in the background. Each cluster provisioning typically takes approximately 33 minutes. Once provisioned, you will always have a steady cluster pool to choose from (barring interactions with the dpp-pruner).

You can monitor the status of the deployment in several ways:

AWS Account Console:

Navigate to your AWS account in the configured region (us-east-1 by default).

Look for newly created resources (EC2 instances, Load Balancers, etc.) that correspond to the cluster pool.

OpenShift Namespaces:

Hive will create new namespaces for each cluster it provisions from the pool. These are typically named aws-sno-<randomChar>.

You can grep for these namespaces: oc get ns | grep aws-sno

Within these namespaces, you can inspect pods and view their logs to understand the provisioning progress:

```bash
oc get pods -n aws-sno-<randomChar>
oc logs -f <pod-name> -n aws-sno-<randomChar>
```

Overall Cluster Pool Status:

Check the full status of your Cluster Pool using oc get clusterpool.

`oc get clusterpools`

Look at the SIZE, READY, and STANDBY columns. Hive will work to bring the READY count up to your specified SIZE.

## Claiming an OpenShift Cluster from a Hive Cluster Pool

## Introduction to Cluster Claims

A ClusterClaim is a Kubernetes Custom Resource that you create to request an OpenShift cluster from an existing Hive ClusterPool. When you create a ClusterClaim, Hive selects an available cluster from the pool, assigns it to your claim, and provides you with the necessary details to access it. Once claimed, the cluster is dedicated to your use for the duration of the claim.

Before claiming a cluster, ensure you have the followed the CLI setup at the top of this README.

After everything is configured, you can use the clusterClaim.yaml file in this directory to claim a cluster. You can change the name if you so wish but the namespace and clusterPoolName must be correct.

`oc apply -f clusterClaim.yaml`

You now have successfully claimed a cluster from the cluster pool!

Afterwards, you will need to run the script in this directory to output the appropriate details for proper cluster usage such as the URL, login details, and kubeconfig certificates.

The script takes in the claim name as the argument, that you defined within the clusterClaim file.

`./creds rhtas-cluster`
