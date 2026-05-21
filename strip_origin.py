"""mitmproxy addon: strip identifying headers from outbound api.anthropic.com requests."""

import logging

from mitmproxy import http

logger = logging.getLogger(__name__)

TARGET_HOST = "api.anthropic.com"
STRIP_HEADERS = ("origin", "anthropic-dangerous-direct-browser-access")


def load(loader):
    logger.info(f"[strip-origin] addon loaded — target={TARGET_HOST}")


def request(flow: http.HTTPFlow) -> None:
    if flow.request.pretty_host != TARGET_HOST:
        return
    stripped = [name for name in STRIP_HEADERS if name in flow.request.headers]
    for name in stripped:
        del flow.request.headers[name]
    if stripped:
        logger.info(
            f"[strip-origin] {flow.request.method} {flow.request.path} "
            f"— stripped: {', '.join(stripped)}"
        )
