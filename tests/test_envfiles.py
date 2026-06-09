from cai.envfiles import (
    find_nearest_env_file,
    get_env_load_candidates,
    get_env_write_target,
)


def test_env_load_candidates_prefer_explicit_then_nearest_then_shared(monkeypatch, tmp_path):
    root = tmp_path / "repo"
    child = root / "nested" / "deeper"
    child.mkdir(parents=True)

    nearest = root / ".env"
    nearest.write_text("CAI_MODEL=alias1\n", encoding="utf-8")

    explicit = tmp_path / "explicit.env"
    explicit.write_text("CAI_MODEL=alias2\n", encoding="utf-8")

    shared = tmp_path / "shared.env"

    monkeypatch.setenv("CAI_ENV_FILE", str(explicit))
    monkeypatch.setattr("cai.envfiles.DEFAULT_SHARED_ENV_PATH", shared)

    candidates = get_env_load_candidates(child)

    assert candidates == [explicit, nearest, shared]


def test_find_nearest_env_file_searches_parent_directories(tmp_path):
    root = tmp_path / "workspace"
    leaf = root / "a" / "b"
    leaf.mkdir(parents=True)

    env_file = root / ".env"
    env_file.write_text("ALIAS_API_KEY=test\n", encoding="utf-8")

    assert find_nearest_env_file(leaf) == env_file


def test_env_write_target_falls_back_to_shared_path(monkeypatch, tmp_path):
    monkeypatch.delenv("CAI_ENV_FILE", raising=False)
    monkeypatch.setattr("cai.envfiles.DEFAULT_SHARED_ENV_PATH", tmp_path / "shared.env")

    target = get_env_write_target(tmp_path / "no-env-here")

    assert target == tmp_path / "shared.env"
