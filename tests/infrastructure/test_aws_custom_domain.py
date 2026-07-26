from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAIN_TEMPLATE = PROJECT_ROOT / "infrastructure" / "aws" / "template.yaml"
CERTIFICATE_TEMPLATE = (
    PROJECT_ROOT / "infrastructure" / "aws" / "certificate-template.yaml"
)
MAKEFILE = PROJECT_ROOT / "Makefile"


def test_cloudfront_uses_custom_domain_certificate_and_route53_aliases():
    template = MAIN_TEMPLATE.read_text()

    assert "DomainName:" in template
    assert "CertificateArn:" in template
    assert "Aliases:" in template
    assert "AcmCertificateArn: !Ref CertificateArn" in template
    assert "SslSupportMethod: sni-only" in template
    assert "Type: AWS::Route53::RecordSet" in template
    assert 'Value: !Sub "https://${DomainName}"' in template


def test_certificate_is_managed_in_a_dedicated_us_east_1_stack():
    certificate_template = CERTIFICATE_TEMPLATE.read_text()
    makefile = MAKEFILE.read_text()

    assert "Type: AWS::CertificateManager::Certificate" in certificate_template
    assert "ValidationMethod: DNS" in certificate_template
    assert "CERTIFICATE_REGION := us-east-1" in makefile
    assert "deploy_certificate:" in makefile
    assert "deploy_backend: deploy_certificate package_infra" in makefile


def test_application_resources_remain_in_ireland_by_default():
    makefile = MAKEFILE.read_text()

    assert "AWS_REGION ?= eu-west-1" in makefile
    assert "DOMAIN_NAME ?= normativa-precheck.endrokosai.com" in makefile


def test_lambdas_do_not_require_reserved_concurrency_quota():
    template = MAIN_TEMPLATE.read_text()

    assert "ReservedConcurrentExecutions:" not in template
