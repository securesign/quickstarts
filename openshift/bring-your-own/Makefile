# Default domain value (can be overridden when calling make)
APPS_DOMAIN := $(shell kubectl get ingress.config.openshift.io cluster -o jsonpath='{.spec.domain}')
export APPS_DOMAIN

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

install-mariadb:
	kustomize build --enable-helm ../shared/database/mariadb | kubectl apply -f -

build: $(TARGET_DIR)
	kustomize build . | envsubst '$${APPS_DOMAIN}' > target/installer.yaml

deploy: build
	kubectl apply -f target/installer.yaml


deploy-all: install-keycloak install-mariadb deploy

# Clean up generated files
clean:
	rm -fr $(TARGET_DIR)
