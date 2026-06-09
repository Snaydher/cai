from cai.tools.misc.agent_discovery import _analyze_task_requirements


def test_analyze_task_requirements_prefers_operational_agents_for_host_scans():
    result = _analyze_task_requirements("Faça uma varredura nmap no host 10.10.10.9 e enumere portas e serviços")
    assert "penetration_testing" in result["detected_categories"]
    assert "network_security" in result["detected_categories"]
    assert any("redteam_agent" in item or "one_tool_agent" in item for item in result["recommendations"])


def test_analyze_task_requirements_prefers_dfir_for_artifact_triage():
    result = _analyze_task_requirements("Analise logs e artefatos de incidente a partir deste pcap e journalctl")
    assert "forensics" in result["detected_categories"]
    assert any("dfir_agent" in item for item in result["recommendations"])
