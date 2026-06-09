from unittest.mock import patch

import pytest

from cai.tools.reconnaissance import nmap as nmap_module


def test_build_nmap_scan_command_defaults():
    command = nmap_module.build_nmap_scan_command("10.10.10.9")
    assert command.startswith("nmap -Pn -T4 --top-ports 1000 -sV -sC")
    assert command.endswith("10.10.10.9")


def test_build_nmap_scan_command_rejects_conflicting_port_modes():
    with pytest.raises(ValueError):
        nmap_module.build_nmap_scan_command("10.10.10.9", ports="80", top_ports=100)


def test_summarize_nmap_output_parses_open_ports():
    output = """Nmap scan report for 10.10.10.9
Host is up (0.11s latency).
22/tcp open ssh OpenSSH 8.2p1
80/tcp open http nginx
"""
    summary = nmap_module.summarize_nmap_output(output)
    assert "Target: 10.10.10.9" in summary
    assert "Open ports: 2" in summary
    assert "22/tcp open ssh" in summary


@patch("cai.tools.reconnaissance.nmap.run_command")
def test_nmap_scan_tool_returns_summary_and_raw_output(mock_run):
    mock_run.return_value = """Nmap scan report for 10.10.10.9
Host is up (0.11s latency).
22/tcp open ssh OpenSSH 8.2p1
80/tcp open http nginx
"""
    result = nmap_module.nmap_scan_impl("10.10.10.9", top_ports=100)
    assert "Open ports: 2" in result
    assert "Raw output:" in result
    mock_run.assert_called_once()
