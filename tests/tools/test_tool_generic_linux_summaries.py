from cai.tools.reconnaissance import generic_linux_command as glc


def test_summarize_command_output_for_nmap():
    result = """Nmap scan report for 10.10.10.9
22/tcp open ssh OpenSSH 8.2p1
80/tcp open http nginx
"""
    summary = glc._summarize_command_output_for_model(result, "nmap -Pn -sV 10.10.10.9")
    assert "Nmap summary:" in summary
    assert "open_ports=2" in summary


def test_summarize_command_output_for_listing():
    result = "a.txt\nb.txt\nc.txt\n"
    summary = glc._summarize_command_output_for_model(result, "ls -la")
    assert "Directory listing: 3 entries" in summary
    assert "- a.txt" in summary
