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

check-gateway-api-crds:
	@if kubectl get crd gateways.gateway.networking.k8s.io >/dev/null 2>&1; then \
	  echo "Gateway API CRDs are available."; \
	else \
	  echo "ERROR: Gateway API CRDs are not installed."; \
	  echo "This quickstart requires OpenShift 4.19+ which includes Gateway API CRDs."; \
	  exit 1; \
	fi

install-ossm:
	kustomize build ../shared/ossm/operator | kubectl apply -f -

wait-for-istio-crd:
	@echo "Waiting for Istio CRD to be available..."
	@while ! kubectl get crd istios.sailoperator.io >/dev/null 2>&1; do \
	  echo "Istio CRD not available yet. Waiting 5 seconds..."; \
	  sleep 5; \
	done
	@echo "Istio CRD is available."

install-istio:
	kustomize build ../shared/ossm/instances | kubectl apply -f -

wait-for-istio-ready:
	@echo "Waiting for Istio to be ready..."
	@while ! kubectl get istio default -n istio-system -o jsonpath='{.status.state}' 2>/dev/null | grep -q "Healthy"; do \
	  echo "Istio not ready yet. Waiting 10 seconds..."; \
	  sleep 10; \
	done
	@echo "Istio is ready."

install-kuadrant-operator:
	kustomize build ../shared/kuadrant/operator | kubectl apply -f -

wait-for-kuadrant-crds:
	@echo "Waiting for Kuadrant CRDs to be available..."
	@while ! kubectl get crd kuadrants.kuadrant.io >/dev/null 2>&1; do \
	  echo "Kuadrant CRD not available yet. Waiting 5 seconds..."; \
	  sleep 5; \
	done
	@while ! kubectl get crd authpolicies.kuadrant.io >/dev/null 2>&1; do \
	  echo "AuthPolicy CRD not available yet. Waiting 5 seconds..."; \
	  sleep 5; \
	done
	@while ! kubectl get crd ratelimitpolicies.kuadrant.io >/dev/null 2>&1; do \
	  echo "RateLimitPolicy CRD not available yet. Waiting 5 seconds..."; \
	  sleep 5; \
	done
	@echo "Kuadrant CRDs are available."

install-kuadrant:
	kustomize build ../shared/kuadrant/instances | kubectl apply -f -

wait-for-kuadrant-ready:
	@echo "Waiting for Kuadrant to be ready..."
	@while ! kubectl get kuadrant kuadrant -n kuadrant-system -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null | grep -q "True"; do \
	  echo "Kuadrant not ready yet. Waiting 10 seconds..."; \
	  sleep 10; \
	done
	@echo "Kuadrant is ready."

wait-for-securesign-crd:
	@echo "Waiting for SecureSign CRD to be available..."
	@while ! kubectl get crd securesigns.rhtas.redhat.com >/dev/null 2>&1; do \
	  echo "SecureSign CRD not available yet. Waiting 5 seconds..."; \
	  sleep 5; \
	done
	@echo "SecureSign CRD is available."

# Kustomize build and envsubst in a single step
build: $(TARGET_DIR)
	kustomize build . | envsubst '$${APPS_DOMAIN}' | envsubst '$${SERVICE_ACCOUNT_ISSUER}' > target/installer.yaml

# Apply the processed YAML to the cluster
deploy: build
	kubectl apply -f target/installer.yaml --server-side=true

deploy-all: install-keycloak check-gateway-api-crds install-ossm wait-for-istio-crd install-istio wait-for-istio-ready install-kuadrant-operator wait-for-kuadrant-crds install-kuadrant wait-for-kuadrant-ready wait-for-securesign-crd deploy

# Clean up generated files
clean:
	rm -fr $(TARGET_DIR)
