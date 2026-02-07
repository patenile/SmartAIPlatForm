#!/usr/bin/env python3
"""
Rule config loader for granular rule control.
Reads .smartai_rules.yaml and provides per-file rule settings, suppression, and overrides.
Supports:
- skip_rules: List of rules to skip (per global/folder/file)
- suppressed_rules: List of rules to suppress (temporary or permanent, with reason)
- Per-rule overrides: thresholds, parameters, etc.
Category: automation
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
import yaml
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
parser = get_arg_parser()
args = parser.parse_args()
logger = get_logger(debug=args.debug)

def save_rule_config(config):
    """
    Saves the rule config dict to .smartai_rules.yaml.
    """
    config_path = Path(__file__).parent.parent / ".smartai_rules.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)
    logger.info(f"Rule config saved to {config_path}")


def load_rule_config():
    config_path = Path(__file__).parent.parent / ".smartai_rules.yaml"
    if not config_path.exists():
        return {"max_file_length": 350, "min_coverage": 90, "skip_rules": [], "folders": {}, "suppressed_rules": {}}
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # Ensure suppressed_rules exists
    if "suppressed_rules" not in config:
        config["suppressed_rules"] = {}
    return config

def get_file_rule_settings(file_path, config):
    """
    Returns the effective rule config for a file, including suppression/overrides.
    - file_path: Path object, relative to project root
    - config: loaded config dict
    """
    rel_path = str(file_path.relative_to(Path(__file__).parent.parent))
    for folder, overrides in (config.get("folders") or {}).items():
        if rel_path.startswith(folder):
            merged = {**config, **overrides}
            # Merge suppressed_rules
            if "suppressed_rules" in overrides:
                merged["suppressed_rules"] = {**config.get("suppressed_rules", {}), **overrides["suppressed_rules"]}
            return merged
    return config

def is_rule_suppressed(rule_name, config, file_path=None):
    """
    Returns True if rule_name is suppressed globally or for the given file_path.
    """
    suppressed = config.get("suppressed_rules", {})
    if rule_name in suppressed:
        return True, suppressed[rule_name]
    # Optionally, support per-file suppression in the future
    return False, None

if __name__ == "__main__":
    try:
        config = load_rule_config()
        logger.info(config)
        logger.info(get_file_rule_settings(Path("scripts/check_py_length.py"), config))
        # Demo suppression
        suppressed, reason = is_rule_suppressed("check_py_length", config)
        logger.info(f"Suppressed: {suppressed}, Reason: {reason}")
    except Exception as e:
        logger.error(f"Exception in rule_config demo: {e}")
