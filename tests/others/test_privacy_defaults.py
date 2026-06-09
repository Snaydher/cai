from cai.config import CAIConfig
from cai.internal.components.metrics import process_metrics
from cai.sdk.agents.run_to_jsonl import get_session_recorder


def test_privacy_defaults_disable_tracing_telemetry_and_usage_tracking(monkeypatch):
    monkeypatch.delenv("CAI_TRACING", raising=False)
    monkeypatch.delenv("CAI_TELEMETRY", raising=False)

    cfg = CAIConfig.from_env()

    assert cfg.tracing is False
    assert cfg.telemetry is False


def test_session_recorder_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("CAI_DISABLE_SESSION_RECORDING", raising=False)
    recorder = get_session_recorder()

    assert recorder is not None
    assert recorder.session_id is None
    assert recorder.filename is None
    assert bool(recorder) is False
    recorder.log_user_message("hello")
    recorder.log_assistant_message("world")
    recorder.log_session_end()
    recorder.warning("test %s", "warning")


def test_metrics_upload_is_disabled(monkeypatch, tmp_path):
    metrics_file = tmp_path / "session.jsonl"
    metrics_file.write_text("{}", encoding="utf-8")

    monkeypatch.delenv("CAI_TELEMETRY", raising=False)

    assert process_metrics(str(metrics_file), sid="test-session") is False
