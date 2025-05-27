.PHONY: all deploy clean

NAMESPACE := dex-idp
MANIFESTS := dex-namespace.yaml dex-config.yaml dex-deployment.yaml dex-service.yaml dex-route.yaml

# Command to get the OpenShift cluster's application domain.
CLUSTER_DOMAIN := $(shell kubectl get ingress.config.openshift.io cluster -o jsonpath='{.spec.domain}')
export CLUSTER_DOMAIN

all: deploy

deploy:
	@echo "Detected OpenShift Cluster Domain: $${CLUSTER_DOMAIN}"

	# Copy the template to the active config file before sed
	cp dex-config.yaml.template dex-config.yaml

	sed -i "s|https://dex-idp-route-dex-idp.<your-cluster-domain>|https://dex-idp-route-$(NAMESPACE).${CLUSTER_DOMAIN}|g" dex-config.yaml

	@for file in $(MANIFESTS); do \
		echo "Applying $$file..."; \
		oc apply -f $$file -n $(NAMESPACE); \
	done

	@echo "Access URL: https://dex-idp-route-$(NAMESPACE).$(CLUSTER_DOMAIN)/dex"
	@echo "NOTE: It may take a minute for the route to become active."

clean:
	@echo "--- Deleting $(NAMESPACE) ---"
	kubectl delete namespace $(NAMESPACE)
