# Default domain value (can be overridden when calling make)
APPS_DOMAIN := $(shell kubectl get ingress.config.openshift.io cluster -o jsonpath='{.spec.domain}')

SERVICE_ACCOUNT_ISSUER ?= $(shell kubectl get authentication.config.openshift.io cluster -ojsonpath='{.spec.serviceAccountIssuer}')
ifeq ($(strip $(SERVICE_ACCOUNT_ISSUER)),)
	SERVICE_ACCOUNT_ISSUER := "https://kubernetes.default.svc"
endif

export APPS_DOMAIN
export SERVICE_ACCOUNT_ISSUER

TARGET_DIR := target
# Ensure the target directory exists
$(TARGET_DIR):
	mkdir -p $(TARGET_DIR)

install-keycloak-operator:
	kubectl apply -k 'github.com/securesign/secure-sign-operator/ci/keycloak/operator/base?ref=release-1.1'

# Wait until the CRD is available in the cluster
wait-for-keycloaks-crd:
	@echo "Waiting for CRD 'keycloaks.keycloak.org' to be available..."
	@while ! kubectl get crd keycloaks.keycloak.org >/dev/null 2>&1; do \
	  echo "CRD 'keycloaks.keycloak.org' not available yet. Waiting 5 seconds..."; \
	  sleep 5; \
	done; \
	echo "CRD 'keycloaks.keycloak.org' is now available."

install-keycloak: install-keycloak-operator wait-for-keycloaks-crd
	kubectl apply -k 'github.com/securesign/secure-sign-operator/ci/keycloak/resources/base?ref=release-1.1'

# Kustomize build and envsubst in a single step
build: $(TARGET_DIR)
	kustomize build . | envsubst '$${APPS_DOMAIN}' | envsubst '$${SERVICE_ACCOUNT_ISSUER}' > target/installer.yaml

# Apply the processed YAML to the cluster
deploy: build
	kubectl apply -f target/installer.yaml

deploy-all: install-keycloak deploy

# Clean up generated files
clean:
	rm -fr $(TARGET_DIR)
