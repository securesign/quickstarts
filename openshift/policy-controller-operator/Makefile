ifndef RHTAS_INSTALL_NAMESPACE
  $(error RHTAS_INSTALL_NAMESPACE is not set)
endif

FULCIO_URL ?= $(shell oc -n $(RHTAS_INSTALL_NAMESPACE) get fulcio -o jsonpath='{.items[0].status.url}')
REKOR_URL ?= $(shell oc -n $(RHTAS_INSTALL_NAMESPACE) get rekor -o jsonpath='{.items[0].status.url}')
TUF_URL ?= $(shell oc -n $(RHTAS_INSTALL_NAMESPACE) get tuf -o jsonpath='{.items[0].status.url}')
BASE64_TUF_ROOT ?= $(shell curl -fsSL "$(TUF_URL)/root.json" | base64 -w0)

ifndef OIDC_ISSUER_URL
  $(error OIDC_ISSUER_URL is not set)
endif
ifndef OIDC_SUBJECT
  $(error OIDC_SUBJECT is not set)
endif

TARGET_DIR := target
SHARED_DIR := ../shared/policy-controller

$(TARGET_DIR):
	@mkdir -p $(TARGET_DIR)

build-trust-root: $(TARGET_DIR)
	@export TUF_URL="$(TUF_URL)" BASE64_TUF_ROOT="$(BASE64_TUF_ROOT)" && \
	envsubst '$${TUF_URL} $${BASE64_TUF_ROOT}' < $(SHARED_DIR)/trust-root.yaml > $(TARGET_DIR)/trust-root.yaml

build-cluster-image-policy: $(TARGET_DIR)
	@export FULCIO_URL="$(FULCIO_URL)" REKOR_URL="$(REKOR_URL)" OIDC_ISSUER_URL="$(OIDC_ISSUER_URL)" OIDC_SUBJECT="$(OIDC_SUBJECT)" && \
	envsubst '$${FULCIO_URL} $${REKOR_URL} $${OIDC_ISSUER_URL} $${OIDC_SUBJECT}' < $(SHARED_DIR)/cluster-image-policy.yaml > $(TARGET_DIR)/cluster-image-policy.yaml

build-verify-cronjob: $(TARGET_DIR)
	@export FULCIO_URL="$(FULCIO_URL)" REKOR_URL="$(REKOR_URL)" TUF_URL="$(TUF_URL)" OIDC_ISSUER_URL="$(OIDC_ISSUER_URL)" && \
	envsubst '$${FULCIO_URL} $${REKOR_URL} $${TUF_URL} $${OIDC_ISSUER_URL}' < $(SHARED_DIR)/verify-cronjob.yaml > $(TARGET_DIR)/verify-cronjob.yaml

build-all: $(TARGET_DIR) build-trust-root build-cluster-image-policy build-verify-cronjob
	@cp $(SHARED_DIR)/subscription.yaml $(TARGET_DIR)/subscription.yaml
	@cp $(SHARED_DIR)/namespace.yaml $(TARGET_DIR)/namespace.yaml
	@cp $(SHARED_DIR)/policy-controller.yaml $(TARGET_DIR)/policy-controller.yaml

wait-for-operator-ready:
	@echo "Waiting for policy-controller-operator to be ready..."
	@while true; do \
	  PHASE=$$(oc get csv -n openshift-operators -l operators.coreos.com/policy-controller-operator.openshift-operators -o jsonpath='{.items[0].status.phase}' 2>/dev/null); \
	  if [ "$$PHASE" = "Succeeded" ]; then break; fi; \
	  echo "CSV phase: $${PHASE:-not found}. Waiting 5 seconds..."; \
	  sleep 5; \
	done; \
	echo "Policy controller operator is ready."

wait-for-policy-controller-ready:
	@echo "Waiting for policy controller deployments to be created..."
	@while [ -z "$$(oc get deployments -n policy-controller-operator -o name 2>/dev/null)" ]; do \
	  echo "No deployments found yet. Waiting 5 seconds..."; \
	  sleep 5; \
	done
	@echo "Waiting for policy controller deployments to be ready..."
	@oc wait deployment -n policy-controller-operator --all --for=condition=Available --timeout=120s
	@echo "All policy controller deployments are ready."

deploy-policy-controller-operator: build-all
	oc apply -f $(TARGET_DIR)/subscription.yaml

deploy-policy-controller: build-all
	oc apply -f $(TARGET_DIR)/namespace.yaml -f $(TARGET_DIR)/policy-controller.yaml

deploy-policy-controller-resources: build-all
	oc apply -f $(TARGET_DIR)/trust-root.yaml
	oc apply -f $(TARGET_DIR)/cluster-image-policy.yaml
	oc apply -f $(TARGET_DIR)/verify-cronjob.yaml

deploy-all: deploy-policy-controller-operator wait-for-operator-ready deploy-policy-controller wait-for-policy-controller-ready deploy-policy-controller-resources

undeploy: build-all
	oc delete -f $(TARGET_DIR) --ignore-not-found
	@CSV=$$(oc get csv -n openshift-operators -o name | grep policy-controller-operator); \
	if [ -n "$$CSV" ]; then \
	  echo "Deleting $$CSV..."; \
	  oc delete $$CSV -n openshift-operators; \
	else \
	  echo "No policy-controller-operator CSV found."; \
	fi

clean: $(TARGET_DIR)
	@rm -fr $(TARGET_DIR)
