#!/usr/bin/env python3
"""Generate config.toml from our own config.example.toml, overriding deploy keys.

Unlike the upstream-clone setup, the source here IS our repo (rsync'd to
$DEPLOY_PATH/src by deploy-turbo.yml), so we patch our own config.example.toml.

Env in:
  DEPLOY_PATH              dir containing src/config.example.toml; output written here
  TURBO_DEEPSEEK_API_KEY   DeepSeek API key
  TURBO_PEXELS_API_KEY     Pexels API key
"""
import os
import re
import pathlib

deploy = os.environ["DEPLOY_PATH"]
dk = os.environ["TURBO_DEEPSEEK_API_KEY"]
px = os.environ["TURBO_PEXELS_API_KEY"]
src = pathlib.Path(deploy, "src", "config.example.toml").read_text()

# Fail loud rather than silently dropping a secret: every key we set lives under
# [app], and the insert fallback below anchors on this header. If the config is
# ever restructured and removes it, stop instead of producing a config missing
# our overrides.
assert "[app]" in src, "config.example.toml has no [app] section"


def setkey(text, key, value):
    """Set `key = value` under [app]; replace in place if present, else insert under [app]."""
    pat = re.compile(r"(?m)^(\s*)" + re.escape(key) + r"\s*=.*$")
    new, n = pat.subn(lambda m: f"{m.group(1)}{key} = {value}", text, count=1)
    if n == 0:
        # Key absent — insert it right under [app]. TOML is whitespace-tolerant.
        new = re.sub(
            r"(?m)^(\[app\]\s*)$",
            lambda m: f"{m.group(1)}\n{key} = {value}",
            text,
            count=1,
        )
    return new


src = setkey(src, "llm_provider", '"deepseek"')
src = setkey(src, "deepseek_api_key", f'"{dk}"')
src = setkey(src, "deepseek_base_url", '"https://api.deepseek.com"')
src = setkey(src, "deepseek_model_name", '"deepseek-chat"')
src = setkey(src, "pexels_api_keys", f'["{px}"]')
src = setkey(src, "subtitle_provider", '"edge"')

out = pathlib.Path(deploy, "config.toml")
out.write_text(src)
out.chmod(0o600)
print("config.toml written:", out)
