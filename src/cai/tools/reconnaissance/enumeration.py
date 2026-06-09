"""Structured enumeration wrappers for common operator workflows."""

from __future__ import annotations

from cai.sdk.agents import function_tool
from cai.tool_registry import TOOL_REGISTRY
from cai.tools.common import run_command
from cai.tools.reconnaissance.nmap import nmap_scan_impl
from cai.tools.web.http_probe import http_probe_impl


def enum_network_surface_impl(
    target: str,
    top_ports: int | None = 1000,
    os_detection: bool = False,
    ctf=None,
) -> str:
    """Run a structured first-pass network surface enumeration."""
    scan_result = nmap_scan_impl(
        target=target,
        top_ports=top_ports,
        service_detection=True,
        default_scripts=True,
        os_detection=os_detection,
        aggressive=False,
        udp=False,
        full_tcp=False,
        skip_host_discovery=True,
        timing_template="T4",
        extra_args="",
        ctf=ctf,
    )
    return f"Network surface enumeration:\n{scan_result}"


@function_tool
def enum_network_surface(
    target: str,
    top_ports: int | None = 1000,
    os_detection: bool = False,
    ctf=None,
) -> str:
    """Run a structured first-pass network surface enumeration."""
    return enum_network_surface_impl(
        target=target,
        top_ports=top_ports,
        os_detection=os_detection,
        ctf=ctf,
    )


def enum_web_surface_impl(
    target: str,
    scheme: str = "http",
    ctf=None,
) -> str:
    """Run a structured first-pass web surface enumeration."""
    probe_result = http_probe_impl(
        target=target,
        scheme=scheme,
        method="GET",
        path="/",
        follow_redirects=True,
        verify_tls=False if scheme == "http" else True,
        timeout_seconds=15,
        user_agent="cai-web-enum/1.0",
    )
    headers_result = run_command(
        f"curl -sS -I {scheme}://{target}",
        ctf=ctf,
    )
    return f"Web surface enumeration:\n{probe_result}\n\nHeaders:\n{headers_result}"


@function_tool
def enum_web_surface(
    target: str,
    scheme: str = "http",
    ctf=None,
) -> str:
    """Run a structured first-pass web surface enumeration."""
    return enum_web_surface_impl(target=target, scheme=scheme, ctf=ctf)


TOOL_REGISTRY.register("enum_network_surface", enum_network_surface, categories=["recon", "network"])
TOOL_REGISTRY.register("enum_web_surface", enum_web_surface, categories=["recon", "web", "network"])
