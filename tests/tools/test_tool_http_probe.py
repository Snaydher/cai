from unittest.mock import patch

from cai.tools.web import http_probe as http_probe_module


class _FakeResponse:
    def __init__(self):
        self.url = "https://example.com/"
        self.status_code = 200
        self.headers = {
            "server": "nginx",
            "content-type": "text/html",
            "content-length": "42",
        }
        self.text = "<html><title>Example Domain</title><body>Hello</body></html>"


def test_summarize_http_probe_extracts_title():
    summary = http_probe_module.summarize_http_probe(
        url="https://example.com/",
        status_code=200,
        headers={"server": "nginx", "content-type": "text/html"},
        body="<title>Example Domain</title>",
    )
    assert "Status: 200" in summary
    assert "Title: Example Domain" in summary


@patch("cai.tools.web.http_probe.httpx.request")
def test_http_probe_tool_returns_summary_and_preview(mock_request):
    mock_request.return_value = _FakeResponse()
    result = http_probe_module.http_probe_impl("example.com", scheme="https")
    assert "URL: https://example.com/" in result
    assert "Status: 200" in result
    assert "Title: Example Domain" in result
    assert "Body preview:" in result
