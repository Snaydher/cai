# Fork Maintenance

This fork is maintained as a productized derivative, not as a close mirror of upstream.

## Branching

- `main`: clean fallback branch for the fork
- `custom/stable`: primary integration branch for local product work
- `feat/*`, `fix/*`, `exp/*`: short-lived branches off `custom/stable`

## Upstream intake

Use `upstream` as a selective source of patches.

Typical workflow:

```bash
git fetch upstream --prune
git log --oneline custom/stable..upstream/main
git show <commit>
git switch custom/stable
git cherry-pick -x <commit>
```

## Fork-specific behavior

This fork intentionally diverges from upstream in a few important areas.

### Privacy defaults

- telemetry defaults to off
- tracing defaults to off
- session recording defaults to off
- metrics upload is disabled
- startup/privacy messaging about research data collection was removed

Session recording is now opt-in. When it is disabled, CAI uses an internal no-op recorder so the CLI keeps working without local JSONL session logs.

### Environment loading

The runtime now resolves environment files in this order:

1. `CAI_ENV_FILE`
2. nearest `.env` walking upward from the current working directory
3. `~/.config/cai/.env`

This lets the fork use one central env file across many work directories while still supporting project-local overrides.

### Authentication rules

OpenAI-compatible key resolution is now explicit:

- `alias*`, `cai*`, `csi*` models use `ALIAS_API_KEY`
- other OpenAI-compatible models such as `gpt-*` and `zai/*` use `OPENAI_API_KEY`
- placeholder keys are only allowed in a few client-bootstrap paths and are not relied on for real provider authentication

If a provider rejects a request with `401`, validate the real key against the provider directly before debugging CAI.

### Operational terminal improvements

The fork adds structured tools and better terminal ergonomics:

- `nmap_scan`: validated nmap interface with structured arguments
- `http_probe`: first-pass HTTP(S) probe with compact summary
- `enum_network_surface`: structured network enumeration wrapper
- `enum_web_surface`: structured web enumeration wrapper
- richer shell session summaries: cwd, command count, last input
- output summarizers for `nmap`, HTTP-like output, listings, and socket tables

These tools are wired into the main operational agents so users can keep issuing natural-language requests while the model prefers structured tools over free-form shell when appropriate.

## Customization guidance

Prefer new layers over edits to volatile upstream files:

- `src/cai/agents/personal/` for fork-specific agents
- `config/fork-presets/` for YAML and startup presets
- wrapper scripts and docs for local workflows
- structured tools under `src/cai/tools/`

Avoid heavy edits in these areas unless required:

- `src/cai/cli_headless.py`
- `src/cai/repl/`
- `src/cai/tui/`
- `src/cai/prompts/`
- central upstream agents

## Local runtime

This fork is intended to run from source, using its own local virtual environment.

Useful commands:

```bash
# recreate/install the local venv
scripts/bootstrap-local-venv.sh

# run the fork directly from source
scripts/use-local-cai.sh
```

Recommended shell setup:

```bash
export PATH="/home/snyder/Data/cai/.venv/bin:$PATH"
export CAI_ENV_FILE="$HOME/.config/cai/.env"
```

Recommended central env layout:

```bash
CAI_MODEL=zai/glm-4.5-flash
OPENAI_API_KEY=<provider-key>
```

For Alias-hosted models:

```bash
CAI_MODEL=alias1
ALIAS_API_KEY=<alias-key>
```

During migration, avoid removing the old CAI installation until the local fork starts successfully and basic commands work.
