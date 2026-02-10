"""
Secrets helper.

Fetches secrets from AWS Secrets Manager in production,
falls back to environment variables for local development.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)


def get_secret(key: str, *, secret_name: str | None = None, region: str | None = None) -> str:
    """
    Retrieve a secret value by *key*.

    Resolution order:
      1. AWS Secrets Manager (if ``secret_name`` is set and boto3 is available)
      2. Environment variable matching *key*

    Parameters
    ----------
    key : str
        The JSON key inside the secret **and** the fallback env-var name
        (e.g. ``"OPENAI_API_KEY"``).
    secret_name : str | None
        Secrets Manager secret name.  Defaults to the ``OPENAI_SECRET_NAME``
        env var.  When empty/None, Secrets Manager is skipped entirely.
    region : str | None
        AWS region.  Defaults to ``AWS_DEFAULT_REGION`` env var.

    Returns
    -------
    str
        The secret value, or an empty string if not found anywhere.
    """
    secret_name = secret_name or os.getenv("OPENAI_SECRET_NAME", "")
    region = region or os.getenv("AWS_DEFAULT_REGION", "")

    # ── Try Secrets Manager first ────────────────────────────────
    if secret_name:
        try:
            import boto3  # noqa: delay import so local dev doesn't need boto3

            client = boto3.client("secretsmanager", region_name=region or None)
            resp = client.get_secret_value(SecretId=secret_name)
            payload = json.loads(resp["SecretString"])
            value = payload.get(key, "")
            if value:
                logger.info("Loaded %s from Secrets Manager (%s)", key, secret_name)
                return value
        except ImportError:
            logger.debug("boto3 not installed — skipping Secrets Manager")
        except Exception as exc:
            logger.warning("Secrets Manager lookup failed: %s", exc)

    # ── Fall back to environment variable ────────────────────────
    value = os.getenv(key, "")
    if value:
        logger.info("Loaded %s from environment variable", key)
    return value
