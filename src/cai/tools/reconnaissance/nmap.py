"""Structured nmap tooling for operational agents."""

from __future__ import annotations

import re
import shlex

from cai.sdk.agents import function_tool
from cai.tools.common import run_command
from cai.tool_registry import TOOL_REGISTRY

_VALID_TIMING_TEMPLATES = {"T0", "T1", "T2", "T3", "T4", "T5"}


def _normalize_timing_template(timing_template: str) -> str:
    timing = (timing_template or "T4").strip().upper()
    if timing not in _VALID_TIMING_TEMPLATES:
        raise ValueError(f"Invalid timing template: {timing_template}")
    return timing


def _sanitize_extra_args(extra_args: str) -> str:
    extra = (extra_args or "").strip()
    if not extra:
        return ""
    if any(token in extra for token in ("&&", "||", ";", "`", "$(")):
        raise ValueError("extra_args contains unsupported shell control operators")
    return extra


def build_nmap_scan_command(
    target: str,
    *,
    ports: str = "",
    top_ports: int | None = 1000,
    service_detection: bool = True,
    default_scripts: bool = True,
    os_detection: bool = False,
    aggressive: bool = False,
    udp: bool = False,
    full_tcp: bool = False,
    skip_host_discovery: bool = True,
    timing_template: str = "T4",
    extra_args: str = "",
) -> str:
    """Build a validated nmap command line."""
    normalized_target = (target or "").strip()
    if not normalized_target:
        raise ValueError("target is required")
    if ports and top_ports:
        raise ValueError("ports and top_ports cannot be used together")
    if ports and full_tcp:
        raise ValueError("ports and full_tcp cannot be used together")
    if top_ports is not None and top_ports <= 0:
        raise ValueError("top_ports must be greater than zero")

    args: list[str] = ["nmap"]
    if skip_host_discovery:
        args.append("-Pn")
    args.append(f"-{_normalize_timing_template(timing_template)}")
    if full_tcp:
        args.append("-p-")
    elif ports:
        args.extend(["-p", ports.strip()])
    elif top_ports:
        args.extend(["--top-ports", str(top_ports)])
    if service_detection:
        args.append("-sV")
    if default_scripts:
        args.append("-sC")
    if os_detection:
        args.append("-O")
    if aggressive:
        args.append("-A")
    if udp:
        args.append("-sU")

    extra = _sanitize_extra_args(extra_args)
    if extra:
        args.append(extra)

    args.append(shlex.quote(normalized_target))
    return " ".join(args)


def summarize_nmap_output(output: str) -> str:
    """Extract a compact operator-friendly summary from nmap output."""
    lines = output.splitlines()
    host = ""
    open_ports: list[str] = []
    service_rows: list[str] = []
    host_up = False
    os_guess = ""

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Nmap scan report for "):
            host = stripped.removeprefix("Nmap scan report for ").strip()
        elif "Host is up" in stripped:
            host_up = True
        elif re.match(r"^\d+/(tcp|udp)\s+open", stripped):
            open_ports.append(stripped)
            if len(service_rows) < 8:
                service_rows.append(stripped)
        elif stripped.startswith("OS details:") and not os_guess:
            os_guess = stripped.removeprefix("OS details:").strip()
        elif stripped.startswith("Running:") and not os_guess:
            os_guess = stripped.removeprefix("Running:").strip()

    summary_lines: list[str] = []
    if host:
        summary_lines.append(f"Target: {host}")
    summary_lines.append(f"Host up: {'yes' if host_up else 'unknown'}")
    summary_lines.append(f"Open ports: {len(open_ports)}")
    if service_rows:
        summary_lines.append("Services:")
        summary_lines.extend(f"- {row}" for row in service_rows)
    if os_guess:
        summary_lines.append(f"OS guess: {os_guess}")
    if not open_ports and output.strip():
        summary_lines.append("No open ports parsed from output.")
    return "\n".join(summary_lines)


def nmap_scan_impl(
    target: str,
    ports: str = "",
    top_ports: int | None = 1000,
    service_detection: bool = True,
    default_scripts: bool = True,
    os_detection: bool = False,
    aggressive: bool = False,
    udp: bool = False,
    full_tcp: bool = False,
    skip_host_discovery: bool = True,
    timing_template: str = "T4",
    extra_args: str = "",
    ctf=None,
) -> str:
    """Run a structured nmap scan and return a compact summary plus raw output."""
    command = build_nmap_scan_command(
        target,
        ports=ports,
        top_ports=top_ports,
        service_detection=service_detection,
        default_scripts=default_scripts,
        os_detection=os_detection,
        aggressive=aggressive,
        udp=udp,
        full_tcp=full_tcp,
        skip_host_discovery=skip_host_discovery,
        timing_template=timing_template,
        extra_args=extra_args,
    )
    raw_output = run_command(command, ctf=ctf, stream=True)
    summary = summarize_nmap_output(raw_output)
    return f"{summary}\n\nRaw output:\n{raw_output}"


@function_tool
def nmap_scan(
    target: str,
    ports: str = "",
    top_ports: int | None = 1000,
    service_detection: bool = True,
    default_scripts: bool = True,
    os_detection: bool = False,
    aggressive: bool = False,
    udp: bool = False,
    full_tcp: bool = False,
    skip_host_discovery: bool = True,
    timing_template: str = "T4",
    extra_args: str = "",
    ctf=None,
) -> str:
    """Run a structured nmap scan and return a compact summary plus raw output."""
    return nmap_scan_impl(
        target=target,
        ports=ports,
        top_ports=top_ports,
        service_detection=service_detection,
        default_scripts=default_scripts,
        os_detection=os_detection,
        aggressive=aggressive,
        udp=udp,
        full_tcp=full_tcp,
        skip_host_discovery=skip_host_discovery,
        timing_template=timing_template,
        extra_args=extra_args,
        ctf=ctf,
    )


@function_tool
def nmap(args: str, target: str, ctf=None) -> str:
    """Backward-compatible raw nmap wrapper for legacy prompts and tests."""
    command = f"nmap {(args or '').strip()} {shlex.quote((target or '').strip())}".strip()
    return run_command(command, ctf=ctf, stream=True)


TOOL_REGISTRY.register("nmap_scan", nmap_scan, categories=["recon", "network"])
TOOL_REGISTRY.register("nmap", nmap, categories=["recon", "network"])
