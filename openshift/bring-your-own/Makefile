# Default domain value (can be overridden when calling make)
SHELL := /bin/bash -eu -o pipefail
APPS_DOMAIN := $(shell kubectl get ingress.config.openshift.io cluster -o jsonpath='{.spec.domain}')
export APPS_DOMAIN

TARGET_DIR := target
# Ensure the target directory exists
$(TARGET_DIR):
	mkdir -p $(TARGET_DIR)

.PHONY: generate-keys check-keys
generate-keys: target/ctlog.pub

target/ctlog.pub: target/.ready
	openssl pkey -in target/ctlog.key -pubout -out target/ctlog.pub

target/.ready:
	@umask 077; mkdir -p target; \
	for name in fulcio ctlog rekor tsa-root tsa; do \
	  openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:prime256v1 -out target/$$name.key; \
	done
	openssl req -new -x509 -key target/fulcio.key -days 365 -subj '/O=RHTAS Demo/CN=Fulcio CA' -config certificates.cnf -extensions ca -out target/fulcio.crt
	openssl req -new -x509 -key target/tsa-root.key -days 365 -subj '/O=RHTAS Demo/CN=TSA CA' -config certificates.cnf -extensions ca -out target/tsa-root.crt
	openssl req -new -key target/tsa.key -subj '/O=RHTAS Demo/CN=TSA' -out target/tsa.csr
	openssl x509 -req -in target/tsa.csr -CA target/tsa-root.crt -CAkey target/tsa-root.key -CAcreateserial -days 365 -extfile certificates.cnf -extensions timestamp -out target/tsa.crt
	cat target/tsa.crt target/tsa-root.crt > target/tsa-chain.pem
	touch target/.ready

check-keys: generate-keys
	openssl x509 -in target/fulcio.crt -checkend 0 -noout
	openssl verify -CAfile target/fulcio.crt target/fulcio.crt
	openssl verify -purpose timestampsign -CAfile target/tsa-root.crt target/tsa.crt
	diff target/tsa-chain.pem <(cat target/tsa.crt target/tsa-root.crt)
	@for name in fulcio tsa; do \
	  diff <(openssl pkey -in target/$$name.key -pubout) <(openssl x509 -in target/$$name.crt -pubkey -noout); \
	done
	@for name in ctlog rekor; do openssl pkey -in target/$$name.key -noout; done
	diff target/ctlog.pub <(openssl pkey -in target/ctlog.key -pubout)

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

# Using Red Hat SCLORG MariaDB image (registry.redhat.io/rhel9/mariadb-1011)
# instead of Bitnami due to Bitnami's move to paid subscription model.
# See: https://github.com/bitnami/charts/issues/35164
install-mariadb:
	kustomize build ../shared/database/mariadb | kubectl apply -f -

build: $(TARGET_DIR) check-keys
	kustomize build . | envsubst '$${APPS_DOMAIN}' > target/installer.yaml

deploy: build
	kubectl apply -f target/installer.yaml


deploy-all: install-keycloak install-mariadb deploy

# Clean up generated files
clean:
	rm -fr $(TARGET_DIR)
