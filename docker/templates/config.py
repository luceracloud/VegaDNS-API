#!/usr/bin/env python3
"""
config.py - configures vegadns2 from the environment variables
"""
from __future__ import print_function
import os
import sys

import pystache
from netaddr import IPSet


def pem_is_valid(pem):
    if pem:
        lines = pem.split('\n')
        return (len(lines) > 2
            and "-----BEGIN CERTIFICATE-----" in lines[0]
            and "-----END CERTIFICATE-----" in lines[-1])
        print("SECRET_DB_CA_CERT env variable contains invalid MySQL CA certficate PEM", file=sys.stderr)
    return False

directory = os.path.dirname(os.path.realpath(__file__))
def main():
    db_ssl_ca_cert = os.getenv("SECRET_DB_CA_CERT")
    db_ssl_ca_file = os.getenv("DB_CA_FILE")

    if pem_is_valid(db_ssl_ca_cert) and db_ssl_ca_file:
        try:
            with open(db_ssl_ca_file, 'w') as f:
                f.write(db_ssl_ca_cert)
        except Exception as err:
            print("Problem writing MySQL CA certficate file", err, file=sys.stderr)
            sys.exit(1)
    else:
        # Reset db_ssl_ca_file if we're missing one or more environment variables for SSL
        # to avoid adding an empty 'ssl_ca' option to the local.ini config.
        if not db_ssl_ca_file:
            print("DB_CA_FILE env variable undefined, skipping MySQL SSL config.", file=sys.stderr)
        if not db_ssl_ca_cert:
            print("SECRET_DB_CA_CERT env variable undefined, skipping MySQL SSL config.", file=sys.stderr)
            db_ssl_ca_file = None

    # Verify that we can parse the TRUSTED_IPS list
    trusted_ips = os.getenv("TRUSTED_IPS", default="127.0.0.1")
    trusted_ips = "".join(trusted_ips.split()) # remove whitespace
    trusted_list = trusted_ips.split(',')

    try:
        trusted_ip_range = IPSet(trusted_list)
    except Exception as e:
        print(trusted_list, e, file=sys.stderr)
        print("Problem parsing TRUSTED_IPS environment variable", file=sys.stderr)
        sys.exit(1)

    try:
        config = {
            "db_host": os.getenv("DB_HOST", default="localhost"),
            "db_user": os.getenv("DB_USER", default="vegadns"),
            "db_pass": os.getenv("SECRET_DB_PASS", default="secret"),
            "db_db": os.getenv("DB_DB", default="vegadns"),
            "db_ssl_ca": db_ssl_ca_file,
            "vegadns_generation": os.getenv("VEGADNS_GENERATION", default=""),
            "vegadns": os.getenv("VEGADNS", default="http://127.0.0.1/1.0/export/tinydns"),
            "trusted_ips": trusted_ips,
            "ui_url": os.getenv("UI_URL", default="http://localhost:8080"),
            "email_method": os.getenv("EMAIL_METHOD", default="smtp"),
            "smtp_host": os.getenv("SMTP_HOST", default="localhost"),
            "smtp_port": os.getenv("SMTP_PORT", default="25"),
            "smtp_auth": os.getenv("SMTP_AUTH", default="false"),
            "smtp_user": os.getenv("SMTP_USER", default=""),
            "smtp_password": os.getenv("SECRET_SMTP_PASSWORD", default=""),
            "smtp_tls": os.getenv("SMTP_TLS", default="false"),
            "smtp_ssl": os.getenv("SMTP_SSL", default="false"),
            "smtp_keyfile": os.getenv("SMTP_KEYFILE", default=""),
            "smtp_certfile": os.getenv("SMTP_CERTFILE", default=""),
            "support_name": os.getenv("SUPPORT_NAME", default="The VegaDNS Team"),
            "support_email": os.getenv("SUPPORT_EMAIL", default="support@example.com"),
            "acl_labels": os.getenv("ACL_LABELS", default=""),
            "acl_emails": os.getenv("ACL_EMAILS", default=""),
            "enable_redis_notifications": os.getenv("ENABLE_REDIS_NOTIFICATIONS", default="false"),
            "redis_host": os.getenv("REDIS_HOST", default="127.0.0.1"),
            "redis_port": os.getenv("REDIS_PORT", default="6379"),
            "redis_channel": os.getenv("REDIS_CHANNEL", default="VEGADNS-CHANGES"),
            "enable_consul_notifications": os.getenv("ENABLE_CONSUL_NOTIFICATIONS", default="false"),
            "consul_host": os.getenv("CONSUL_HOST", default="127.0.0.1"),
            "consul_port": os.getenv("CONSUL_PORT", default="8500"),
            "consul_scheme": os.getenv("CONSUL_SCHEME", default="http"),
            "consul_verify_ssl": os.getenv("CONSUL_VERIFY_SSL", default=True),
            "consul_token": os.getenv("CONSUL_TOKEN", default=None),
            "consul_key": os.getenv("CONSUL_KEY", default="VEGADNS-CHANGES"),
            "oidc_enabled": os.getenv("OIDC_ENABLED", default="false"),
            "oidc_issuer": os.getenv("OIDC_ISSUER", default=""),
            "oidc_client": os.getenv("OIDC_CLIENT", default=""),
            "oidc_redirect_uri": os.getenv("OIDC_REDIRECT_URI", default=""),
            "oidc_ui_endpoint": os.getenv("OIDC_UI_ENDPOINT", default=""),
            "oidc_secret": os.getenv("SECRET_OIDC_SECRET", default=""),
            "oidc_scope": os.getenv("OIDC_SCOPE", default="openid,profile,email"),
            "oidc_email_key": os.getenv("OIDC_EMAIL_KEY", default="email"),
            "oidc_groups_key": os.getenv("OIDC_GROUPS_KEY", default="memberof"),
            "oidc_required_group": os.getenv("OIDC_REQUIRED_GROUP", default=""),
            "oidc_firstname_key": os.getenv("OIDC_FIRSTNAME_KEY", default="given_name"),
            "oidc_lastname_key": os.getenv("OIDC_LASTNAME_KEY", default="family_name"),
            "oidc_phone_key": os.getenv("OIDC_PHONE_KEY", default=""),
            "cookie_secret": os.getenv("SECRET_COOKIE_SECRET", default="")
        }
        if config['oidc_enabled'] and not config['cookie_secret']:
            # Running in OIDC mode without setting a secret is very insecure!
            raise ValueError("Cookie secret is required when OIDC is enabled")
    except Exception as err:
        print("Problem reading environment", err, file=sys.stderr)
        sys.exit(1)

    # optionally use first argument as template, path is still
    # relative to this script
    template_file = "./local.ini.template"
    if len(sys.argv) > 1:
        template_file = sys.argv[1]

    try:
        with open(directory + "/" + template_file) as template:
            print(pystache.render(template.read(), config))
    except Exception as err:
        print("Problem rendering template:", err, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
