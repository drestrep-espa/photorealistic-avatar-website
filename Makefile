SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

AWS_REGION ?= eu-west-1
AWS_PROFILE ?=
STACK_NAME ?= normativa-precheck
CERTIFICATE_STACK_NAME ?= $(STACK_NAME)-certificate
CERTIFICATE_REGION := us-east-1
DOMAIN_NAME ?= normativa-precheck.endrokosai.com
HOSTED_ZONE_ID ?= Z02223832U2M8HYJCXSFK
OPENAI_API_KEY_PARAMETER ?= /normativa-precheck/openai-api-key
VECTOR_STORE_ID_PARAMETER ?= /normativa-precheck/vector-store-id

BUILD_DIR := build
LAMBDA_BUILD_DIR := $(BUILD_DIR)/lambda
PACKAGED_TEMPLATE := $(BUILD_DIR)/packaged.yaml
ARTIFACT_BUCKET_FILE := $(BUILD_DIR)/artifact-bucket-name
TEMPLATE := infrastructure/aws/template.yaml
CERTIFICATE_TEMPLATE := infrastructure/aws/certificate-template.yaml

AWS := aws --region $(AWS_REGION) $(if $(AWS_PROFILE),--profile $(AWS_PROFILE),)
AWS_CERTIFICATE := aws --region $(CERTIFICATE_REGION) $(if $(AWS_PROFILE),--profile $(AWS_PROFILE),)

.PHONY: help check_aws check_ssm deploy_certificate build_lambdas package_infra deploy_backend deploy_front deploy_all

help:
	@echo "make deploy_backend  Empaqueta y despliega buckets y Lambdas"
	@echo "make deploy_front    Compila React, sincroniza S3 e invalida CloudFront"
	@echo "make deploy_all      Ejecuta backend y frontend en orden"

check_aws:
	@command -v aws >/dev/null || { echo "Falta AWS CLI."; exit 1; }
	@$(AWS) sts get-caller-identity >/dev/null

check_ssm: check_aws
	@$(AWS) ssm get-parameter \
		--name "$(OPENAI_API_KEY_PARAMETER)" \
		--with-decryption \
		--query Parameter.Name \
		--output text >/dev/null
	@$(AWS) ssm get-parameter \
		--name "$(VECTOR_STORE_ID_PARAMETER)" \
		--query Parameter.Name \
		--output text >/dev/null

deploy_certificate: check_aws
	@$(AWS_CERTIFICATE) cloudformation deploy \
		--template-file "$(CERTIFICATE_TEMPLATE)" \
		--stack-name "$(CERTIFICATE_STACK_NAME)" \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			DomainName="$(DOMAIN_NAME)" \
			HostedZoneId="$(HOSTED_ZONE_ID)"

build_lambdas:
	@rm -rf "$(LAMBDA_BUILD_DIR)"
	@mkdir -p "$(LAMBDA_BUILD_DIR)"
	@.venv/bin/python -m pip install \
		--requirement requirements-lambda.txt \
		--target "$(LAMBDA_BUILD_DIR)" \
		--upgrade
	@cp -R src "$(LAMBDA_BUILD_DIR)/src"
	@test -f /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
	@test -f /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
	@mkdir -p "$(LAMBDA_BUILD_DIR)/fonts"
	@cp /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf "$(LAMBDA_BUILD_DIR)/fonts/"
	@cp /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf "$(LAMBDA_BUILD_DIR)/fonts/"

package_infra: check_ssm build_lambdas
	@mkdir -p "$(BUILD_DIR)"
	@account_id="$$( $(AWS) sts get-caller-identity --query Account --output text )"; \
	artifact_bucket="$$account_id-$(STACK_NAME)-deploy-$(AWS_REGION)"; \
	if ! $(AWS) s3api head-bucket --bucket "$$artifact_bucket" >/dev/null 2>&1; then \
		$(AWS) s3 mb "s3://$$artifact_bucket"; \
	fi; \
	echo "$$artifact_bucket" > "$(ARTIFACT_BUCKET_FILE)"; \
	$(AWS) cloudformation package \
		--template-file "$(TEMPLATE)" \
		--s3-bucket "$$artifact_bucket" \
		--output-template-file "$(PACKAGED_TEMPLATE)"

deploy_backend: deploy_certificate package_infra
	@certificate_arn="$$( $(AWS_CERTIFICATE) cloudformation describe-stacks \
		--stack-name "$(CERTIFICATE_STACK_NAME)" \
		--query "Stacks[0].Outputs[?OutputKey=='CertificateArn'].OutputValue" \
		--output text )"; \
	$(AWS) cloudformation deploy \
		--template-file "$(PACKAGED_TEMPLATE)" \
		--stack-name "$(STACK_NAME)" \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			OpenAiApiKeyParameterName="$(OPENAI_API_KEY_PARAMETER)" \
			VectorStoreIdParameterName="$(VECTOR_STORE_ID_PARAMETER)" \
			DomainName="$(DOMAIN_NAME)" \
			HostedZoneId="$(HOSTED_ZONE_ID)" \
			CertificateArn="$$certificate_arn"

deploy_front: check_aws
	@frontend_bucket="$$( $(AWS) cloudformation describe-stacks \
		--stack-name "$(STACK_NAME)" \
		--query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
		--output text )"; \
	distribution_id="$$( $(AWS) cloudformation describe-stacks \
		--stack-name "$(STACK_NAME)" \
		--query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" \
		--output text )"; \
	frontend_url="$$( $(AWS) cloudformation describe-stacks \
		--stack-name "$(STACK_NAME)" \
		--query "Stacks[0].Outputs[?OutputKey=='FrontendUrl'].OutputValue" \
		--output text )"; \
	chat_url="$$( $(AWS) cloudformation describe-stacks \
		--stack-name "$(STACK_NAME)" \
		--query "Stacks[0].Outputs[?OutputKey=='ChatFunctionUrl'].OutputValue" \
		--output text )"; \
	review_url="$$( $(AWS) cloudformation describe-stacks \
		--stack-name "$(STACK_NAME)" \
		--query "Stacks[0].Outputs[?OutputKey=='ReviewFunctionUrl'].OutputValue" \
		--output text )"; \
	chat_url="$${chat_url%/}"; \
	review_url="$${review_url%/}"; \
	npm ci --prefix frontend; \
	VITE_CHAT_API_URL="$$chat_url" \
	VITE_REVIEW_API_URL="$$review_url" \
		npm run build --prefix frontend; \
	$(AWS) s3 sync frontend/dist "s3://$$frontend_bucket" \
		--delete \
		--exclude index.html \
		--cache-control "public,max-age=31536000,immutable"; \
	$(AWS) s3 cp frontend/dist/index.html "s3://$$frontend_bucket/index.html" \
		--content-type "text/html; charset=utf-8" \
		--cache-control "no-cache,no-store,must-revalidate"; \
	$(AWS) cloudfront create-invalidation \
		--distribution-id "$$distribution_id" \
		--paths "/*" >/dev/null; \
	echo "Frontend publicado en $$frontend_url"

deploy_all: deploy_backend deploy_front
