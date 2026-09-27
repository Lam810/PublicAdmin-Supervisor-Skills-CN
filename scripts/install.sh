#!/usr/bin/env bash
# Install the skills under skills/ into an agent's skills directory.
#
#   scripts/install.sh --target claude            # ~/.claude/skills
#   scripts/install.sh --target claude-project    # ./.claude/skills (current directory)
#   scripts/install.sh --target codex             # ~/.codex/skills
#   scripts/install.sh --target qwen              # ~/.qwen/skills
#   scripts/install.sh --dir /path/to/skills      # any directory
#
# Options:
#   --link          symlink instead of copy (updates follow `git pull`)
#   --only a,b      install only these skills
#   --force         replace existing skills with the same name
#   --dry-run       print what would happen
#
# Each skill directory is self-contained; the repository root is not a skill.
# Directory conventions differ between tools and versions: check your tool's docs.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="$here/skills"
target="" dir="" mode="copy" only="" force=0 dry=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) target="${2:-}"; shift 2 ;;
    --dir) dir="${2:-}"; shift 2 ;;
    --link) mode="link"; shift ;;
    --only) only="${2:-}"; shift 2 ;;
    --force) force=1; shift ;;
    --dry-run) dry=1; shift ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$dir" ]]; then
  case "$target" in
    claude) dir="$HOME/.claude/skills" ;;
    claude-project) dir="$PWD/.claude/skills" ;;
    codex) dir="$HOME/.codex/skills" ;;
    qwen) dir="$HOME/.qwen/skills" ;;
    "") echo "need --target or --dir (see --help)" >&2; exit 2 ;;
    *) echo "unknown target: $target" >&2; exit 2 ;;
  esac
fi

run() { if [[ $dry -eq 1 ]]; then echo "+ $*"; else "$@"; fi; }

run mkdir -p "$dir"
installed=0 skipped=0
for skill in "$src"/*/; do
  name="$(basename "$skill")"
  [[ -f "$skill/SKILL.md" ]] || continue
  if [[ -n "$only" && ",$only," != *",$name,"* ]]; then continue; fi
  dest="$dir/$name"
  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ $force -eq 0 ]]; then
      echo "skip $name (exists; use --force to replace)"; skipped=$((skipped + 1)); continue
    fi
    run rm -rf "$dest"
  fi
  if [[ "$mode" == "link" ]]; then
    run ln -s "${skill%/}" "$dest"
  else
    run cp -R "${skill%/}" "$dest"
  fi
  installed=$((installed + 1))
done
echo "installed $installed skill(s) into $dir ($mode); skipped $skipped"
