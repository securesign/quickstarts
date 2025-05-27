# Dex IDP

An Ansible playbook to install and configure a local **Dex OIDC provider** for use with [Trusted Artifact Signer (TAS)](https://github.com/securesign).  
It prepares a functional identity system to enable artifact signing and verification using `cosign` and TAS.

---

## Overview

This playbook sets up:

- A Dex OIDC identity provider
- Static user connector (username/password)
- A trusted OIDC client for TAS integration
- Dex running on `http://<host>:5556/dex`
- Email and profile claims for downstream validation
- Compatibility with Sigstore's Fulcio, Cosign, and Rekor

---

## Requirements

Before you run this playbook, ensure the following:

- A running target machine (VM, EC2, etc.)
- SSH access to the host
- Python + Ansible installed locally
- Ansible inventory file targeting your host

---

## Usage

### 1. Launch your target host

Provision your machine (e.g., using Terraform, EC2 Console, etc.).

---

### 2. Prepare your Ansible inventory

Create a simple inventory file named `inventory`:

```ini
[rhtas]
13.50.244.205
```

3. Run the playbook

```bash
ansible-playbook -i <path_to_inventory> prepare.yaml -u <remote_user>
```

Dex will now be running on:
http://<HOST_IP>:5556/dex

4. Install TAS with Dex OIDC
Once Dex is ready, configure your TAS playbook to point to it:

```yaml
tas_single_node_fulcio:
  fulcio_config:
    oidc_issuers:
      - issuer: "http://dex-idp:5556/dex"
        url: "http://dex-idp:5556/dex"
        client_id: trusted-artifact-signer
        type: email
```

5. Get an access token

```bash
curl -s -X POST 'http://${OIDC_HOST}:5556/dex/token' \
  -H 'Authorization: Basic dHJ1c3RlZC1hcnRpZmFjdC1zaWduZXI6WlhoaGJYQnNaUzFoY0hBdGMyVmpjbVYw' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=password' \
  --data-urlencode 'scope=openid email profile' \
  --data-urlencode 'username=jdoe@redhat.com' \
  --data-urlencode 'password=secure' \
  | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p'
```

6. Sign and verify artifacts

Sign:

```bash
cosign --verbose sign-blob "$FILENAME.txt" \
  --bundle "$FILENAME.bundle" \
  --identity-token="$TOKEN" \
  --timestamp-server-url="$COSIGN_TSA_URL" \
  --rfc3161-timestamp="$FILENAME.timestamp"
```

Verify:

```bash
cosign --verbose verify-blob \
  --certificate-identity="jdoe@redhat.com" \
  --bundle "${file%.*}.bundle" "$file" \
  --rfc3161-timestamp="${file%.*}.timestamp" \
  --use-signed-timestamps
```

## Notes
This playbook uses a mock/static Dex connector and is not intended for production use.

Designed for use in TAS development and testing workflows.
