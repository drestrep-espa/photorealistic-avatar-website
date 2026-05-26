.DEFAULT_GOAL := help
SHELL := /bin/bash

# ---------- Config ----------
INFRA_DIR    := infra
ENV_FILE     := .env.production.local
AWS_PROFILE  ?=
AWS_FLAGS    := $(if $(AWS_PROFILE),--profile $(AWS_PROFILE),)

# Resolved from `terraform output` (lazy so they're only evaluated when used).
BUCKET          = $(shell cd $(INFRA_DIR) && terraform output -raw psyko_bucket 2>/dev/null)
DISTRIBUTION_ID = $(shell cd $(INFRA_DIR) && terraform output -raw psyko_distribution_id 2>/dev/null)
SITE_URL        = $(shell cd $(INFRA_DIR) && terraform output -raw psyko_url 2>/dev/null)

# ---------- Meta ----------
.PHONY: help
help: ## Show this help
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---------- Preflight ----------
.PHONY: check
check: ## Verify local tooling and required config are present
	@echo "→ Checking local tools..."
	@command -v node      >/dev/null || { echo "  ✗ node not found"; exit 1; }
	@command -v npm       >/dev/null || { echo "  ✗ npm not found"; exit 1; }
	@command -v aws       >/dev/null || { echo "  ✗ aws CLI not found"; exit 1; }
	@command -v terraform >/dev/null || { echo "  ✗ terraform not found (https://developer.hashicorp.com/terraform/install)"; exit 1; }
	@echo "  ✓ node $$(node -v), npm $$(npm -v), aws $$(aws --version 2>&1 | cut -d' ' -f1), terraform $$(terraform version -json | grep -m1 terraform_version | cut -d'"' -f4)"
	@echo "→ Checking AWS credentials..."
	@aws $(AWS_FLAGS) sts get-caller-identity >/dev/null 2>&1 || { echo "  ✗ aws not authenticated. Run 'aws configure' or set AWS_PROFILE."; exit 1; }
	@echo "  ✓ AWS account $$(aws $(AWS_FLAGS) sts get-caller-identity --query Account --output text)"
	@echo "→ Checking build env file..."
	@test -f $(ENV_FILE) || { echo "  ✗ Missing $(ENV_FILE) (copy .env.example and fill VITE_SUPABASE_* values)"; exit 1; }
	@grep -q '^VITE_SUPABASE_URL='      $(ENV_FILE) || { echo "  ✗ VITE_SUPABASE_URL missing in $(ENV_FILE)"; exit 1; }
	@grep -q '^VITE_SUPABASE_ANON_KEY=' $(ENV_FILE) || { echo "  ✗ VITE_SUPABASE_ANON_KEY missing in $(ENV_FILE)"; exit 1; }
	@echo "  ✓ $(ENV_FILE) present"
	@echo "→ Checking Terraform state..."
	@test -d $(INFRA_DIR)/.terraform || { echo "  ! Terraform not initialized — run 'make tf-init' first"; exit 0; }
	@[ -n "$(BUCKET)" ] || { echo "  ! Infra not applied yet — run 'make tf-apply' to create the bucket/distribution"; exit 0; }
	@echo "  ✓ bucket=$(BUCKET)"
	@echo "  ✓ distribution=$(DISTRIBUTION_ID)"
	@echo "  ✓ url=$(SITE_URL)"
	@echo "All checks passed."

# ---------- Terraform ----------
.PHONY: tf-init tf-plan tf-apply tf-destroy tf-output
tf-init: ## terraform init (first time / after provider changes)
	cd $(INFRA_DIR) && terraform init

tf-plan: ## terraform plan
	cd $(INFRA_DIR) && terraform plan

tf-apply: ## terraform apply (creates S3 + CloudFront + ACM + Route 53)
	cd $(INFRA_DIR) && terraform apply

tf-destroy: ## terraform destroy (tears down the infra — careful)
	cd $(INFRA_DIR) && terraform destroy

tf-output: ## Print terraform outputs
	cd $(INFRA_DIR) && terraform output

# ---------- Frontend ----------
.PHONY: install build clean
install: ## npm ci (clean install)
	npm ci

build: ## Build the production bundle to dist/
	@test -f $(ENV_FILE) || { echo "Missing $(ENV_FILE) — copy .env.example and fill it"; exit 1; }
	npm run build

clean: ## Remove dist/ and node_modules/.vite cache
	rm -rf dist node_modules/.vite

# ---------- Deploy ----------
.PHONY: sync invalidate deploy
sync: ## Upload dist/ to S3 (use after `make build`)
	@[ -n "$(BUCKET)" ] || { echo "No bucket output — run 'make tf-apply' first"; exit 1; }
	@test -d dist || { echo "No dist/ — run 'make build' first"; exit 1; }
	aws $(AWS_FLAGS) s3 sync dist/ s3://$(BUCKET)/ \
		--delete \
		--cache-control "public,max-age=31536000,immutable" \
		--exclude "index.html" \
		--exclude "*.html"
	aws $(AWS_FLAGS) s3 sync dist/ s3://$(BUCKET)/ \
		--delete \
		--cache-control "public,max-age=0,must-revalidate" \
		--exclude "*" \
		--include "*.html"

invalidate: ## Invalidate the CloudFront cache (/*)
	@[ -n "$(DISTRIBUTION_ID)" ] || { echo "No distribution output — run 'make tf-apply' first"; exit 1; }
	aws $(AWS_FLAGS) cloudfront create-invalidation \
		--distribution-id $(DISTRIBUTION_ID) \
		--paths "/*" \
		--query 'Invalidation.Id' --output text

deploy: build sync invalidate ## Full deploy: build + sync + invalidate
	@echo "✓ Deployed → $(SITE_URL)"
