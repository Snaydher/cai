from unittest.mock import patch

from cai.tools.reconnaissance import enumeration as enum_module


@patch("cai.tools.reconnaissance.enumeration.nmap_scan_impl")
def test_enum_network_surface_uses_structured_nmap(mock_nmap_scan):
    mock_nmap_scan.return_value = "Target: 10.10.10.9\nOpen ports: 1"
    result = enum_module.enum_network_surface_impl("10.10.10.9")
    assert "Network surface enumeration:" in result
    assert "Open ports: 1" in result
    mock_nmap_scan.assert_called_once()


@patch("cai.tools.reconnaissance.enumeration.run_command")
@patch("cai.tools.reconnaissance.enumeration.http_probe_impl")
def test_enum_web_surface_combines_probe_and_headers(mock_http_probe, mock_run_command):
    mock_http_probe.return_value = "Status: 200\nTitle: Example"
    mock_run_command.return_value = "HTTP/1.1 200 OK\nServer: nginx"
    result = enum_module.enum_web_surface_impl("example.com", scheme="https")
    assert "Web surface enumeration:" in result
    assert "Status: 200" in result
    assert "Headers:" in result
