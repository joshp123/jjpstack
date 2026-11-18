# T3 Code's Codex provider runs this in place of codex (its "Binary path"). It
# hands Codex the T3 override prompt as developer instructions, read from the
# live file at every launch: Codex has no option to read instructions from a
# file, and a copy pasted into T3's settings goes stale. It also pins the
# standard tier as the default, because Codex's /fast toggle writes
# service_tier = "priority" into ~/.codex/config.toml and T3 then defaults
# every Codex thread and sub-agent to fast. A tier picked in T3 still applies.
set -euo pipefail

instructions=$(@jq@ -Rs . < "@overrides@")
exec codex -c "developer_instructions=$instructions" -c 'service_tier="default"' "$@"
