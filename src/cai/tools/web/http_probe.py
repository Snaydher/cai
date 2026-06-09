"""Structured HTTP probing tool for operational agents."""

from __future__ import annotations

import re
from typing import Any

import httpx

from cai.sdk.agents import function_tool
from cai.tool_registry import TOOL_REGISTRY


def _normalize_probe_url(target: str, scheme: str = "http") -> str:
    raw = (target or "").strip()
    if not raw:
        raise ValueError("target is required")
    if "://" in raw:
        return raw
    return f"{scheme}://{raw}"


def summarize_http_probe(
    *,
    url: str,
    status_code: int,
    headers: dict[str, Any],
    body: str,
) -> str:
    """Create a compact summary from an HTTP response."""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
    title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
    server = headers.get("server", "")
    content_type = headers.get("content-type", "")
    location = headers.get("location", "")
    content_length = headers.get("content-length", "")

    lines = [
        f"URL: {url}",
        f"Status: {status_code}",
    ]
    if server:
        lines.append(f"Server: {server}")
    if content_type:
        lines.append(f"Content-Type: {content_type}")
    if content_length:
        lines.append(f"Content-Length: {content_length}")
    if location:
        lines.append(f"Location: {location}")
    if title:
        lines.append(f"Title: {title}")
    return "\n".join(lines)


def http_probe_impl(
    target: str,
    scheme: str = "http",
    method: str = "GET",
    path: str = "/",
    follow_redirects: bool = True,
    verify_tls: bool = True,
    timeout_seconds: int = 15,
    user_agent: str = "cai-http-probe/1.0",
) -> str:
    """Probe an HTTP(S) endpoint and return a compact summary."""
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")
    normalized = _normalize_probe_url(target, scheme=scheme)
    if path and path != "/":
        normalized = normalized.rstrip("/") + "/" + path.lstrip("/")
    response = httpx.request(
        method.upper(),
        normalized,
        headers={"User-Agent": user_agent},
        follow_redirects=follow_redirects,
        verify=verify_tls,
        timeout=timeout_seconds,
    )
    summary = summarize_http_probe(
        url=str(response.url),
        status_code=response.status_code,
        headers=dict(response.headers),
        body=response.text,
    )
    snippet = response.text[:800].strip()
    if snippet:
        return f"{summary}\n\nBody preview:\n{snippet}"
    return summary


@function_tool
def http_probe(
    target: str,
    scheme: str = "http",
    method: str = "GET",
    path: str = "/",
    follow_redirects: bool = True,
    verify_tls: bool = True,
    timeout_seconds: int = 15,
    user_agent: str = "cai-http-probe/1.0",
) -> str:
    """Probe an HTTP(S) endpoint and return a compact summary."""
    return http_probe_impl(
        target=target,
        scheme=scheme,
        method=method,
        path=path,
        follow_redirects=follow_redirects,
        verify_tls=verify_tls,
        timeout_seconds=timeout_seconds,
        user_agent=user_agent,
    )


TOOL_REGISTRY.register("http_probe", http_probe, categories=["recon", "web", "network"])
