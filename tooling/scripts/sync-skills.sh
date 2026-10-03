#!/usr/bin/env bash
#
# One copy of every skill, reachable from every host.
#
# Canonical files live in .github/skills/. Every other host directory holds a symlink into
# it, so "the same SKILL.md in two tools" is a fact about the filesystem rather than a claim
# on a slide. Relative links are used inside the repo, so they survive a clone; git stores
# symlinks natively, which makes them committed artifacts rather than install state.
#
# Why canonical lives under .github/ and not at the root: the lecture's slide shows
# `.github/skills/spec-interrogate/SKILL.md` as the path, and in a repo whose thesis is that
# every artifact shown is real, that must be the real path. It is also the safer bet — of the
# hosts here, Copilot's handling of a symlinked skills directory is the least certain, so it
# gets the real files.
#
# Usage:
#   ./tooling/scripts/sync-skills.sh                 link into the project's host directories
#   ./tooling/scripts/sync-skills.sh --user          also link into $HOME (skills usable in any repo)
#   ./tooling/scripts/sync-skills.sh --check         verify links; exit 1 on drift. For CI.
#   ./tooling/scripts/sync-skills.sh --copy          real copies instead of links (Windows, or hosts
#                                            that do not follow symlinks)
#   ./tooling/scripts/sync-skills.sh --dry-run       print the plan, touch nothing
#   ./tooling/scripts/sync-skills.sh --clean         remove only what this script creates
#   ./tooling/scripts/sync-skills.sh --print <name>  write a skill body to stdout
#   ./tooling/scripts/sync-skills.sh --force         overwrite a real directory (refused by default)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

CANON=".github/skills"
PROJECT_DESTS=(".claude/skills" ".cursor/skills" ".agents/skills")
USER_DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills")
MARKER=".synced-from"

MODE="link"
INCLUDE_USER=0
DRY_RUN=0
FORCE=0
PRINT_SKILL=""

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
plural() { [[ "$1" -eq 1 ]] && printf '%s %s' "$1" "$2" || printf '%s %ss' "$1" "$2"; }
note() { printf '%s\n' "$*" >&2; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)     INCLUDE_USER=1 ;;
    --check)    MODE="check" ;;
    --copy)     MODE="copy" ;;
    --clean)    MODE="clean" ;;
    --dry-run)  DRY_RUN=1 ;;
    --force)    FORCE=1 ;;
    --print)    PRINT_SKILL="${2:-}"; [[ -n "$PRINT_SKILL" ]] || die "--print needs a skill name"; shift ;;
    -h|--help)  sed -n '2,32p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)          die "unknown argument: $1 (try --help)" ;;
  esac
  shift
done

# --- discovery -------------------------------------------------------------------------

[[ -d "$CANON" ]] || die "$CANON does not exist"
[[ -L "$CANON" ]] && die "$CANON is a symlink; it must be the real directory"

discover() {
  local d name
  while IFS= read -r d; do
    name="$(basename "$d")"
    [[ "$name" == _* ]] && continue   # _template is not a skill, and must never register as one
    printf '%s\n' "$name"
  done < <(find "$CANON" -mindepth 2 -maxdepth 2 -name SKILL.md -exec dirname {} \; | sort)
}

# No `mapfile` here on purpose: macOS still ships bash 3.2 as /bin/bash, and this script is
# meant to run on a client's laptop without a Homebrew bash first.
#
# SKILLS is initialised explicitly so `${#SKILLS[@]}` is safe under `set -u` on bash 3.2 even
# when nothing is found. Do NOT write `${#SKILLS[@]-0}` to guard that: it looks like a
# defensive default and it is a syntax error on bash 5, so it passes on macOS and fails in CI.
SKILLS=()
while IFS= read -r _s; do
  [[ -n "$_s" ]] && SKILLS+=("$_s")
done < <(discover)

# --- --print ---------------------------------------------------------------------------

if [[ -n "$PRINT_SKILL" ]]; then
  f="$CANON/$PRINT_SKILL/SKILL.md"
  [[ -f "$f" ]] || die "no such skill: $PRINT_SKILL"
  cat "$f"
  exit 0
fi

if [[ ${#SKILLS[@]} -eq 0 ]]; then
  note "No skills found under $CANON/ yet (directories starting with _ are skipped)."
  note "Nothing to do."
  exit 0
fi

# --- guards ----------------------------------------------------------------------------

# A destination root that is itself a symlink resolving back into the repo would make us
# write per-skill links into our own source tree. Refuse, loudly.
check_dest_root() {
  local root="$1" resolved
  if [[ -L "$root" ]]; then
    resolved="$(cd "$(dirname "$root")" && cd "$(readlink "$root")" 2>/dev/null && pwd || true)"
    if [[ -n "$resolved" && "$resolved" == "$REPO_ROOT"* ]]; then
      die "$root is a symlink into this repo ($resolved). Remove it before syncing."
    fi
  fi
}

# Replace a destination entry only if this script could have made it. A hand-written
# directory is someone's work and is not ours to clobber.
ours() {
  local path="$1"
  [[ -L "$path" ]] && return 0
  [[ -f "$path/$MARKER" ]] && return 0
  return 1
}

# --- refuse to install a skill that breaks the rules we teach ---------------------------

if [[ "$MODE" == "link" || "$MODE" == "copy" ]] && [[ -f tooling/scripts/lint_skills.py ]]; then
  if ! python3 tooling/scripts/lint_skills.py >/dev/null 2>&1; then
    note "lint_skills.py failed. Not installing skills that violate the portability rules"
    note "this repo teaches. Run: python3 tooling/scripts/lint_skills.py"
    exit 1
  fi
fi

# --- the work --------------------------------------------------------------------------

declare -a DESTS=("${PROJECT_DESTS[@]}")
[[ $INCLUDE_USER -eq 1 ]] && DESTS+=("${USER_DESTS[@]}")

status=0
printf '%-22s %-28s %s\n' "SKILL" "ACTION" "DESTINATION"

link_target_for() {
  local dest_root="$1" skill="$2"
  if [[ "$dest_root" == /* ]]; then
    # Outside the repo: relative links cannot reach back, so use an absolute path.
    printf '%s\n' "$REPO_ROOT/$CANON/$skill"
  else
    # Inside the repo: ../../ from <root>/skills/<name> lands at the repo root.
    printf '%s\n' "../../$CANON/$skill"
  fi
}

for dest_root in "${DESTS[@]}"; do
  check_dest_root "$dest_root"

  if [[ "$MODE" != "check" && "$MODE" != "clean" && $DRY_RUN -eq 0 ]]; then
    mkdir -p "$dest_root"
  fi

  for skill in "${SKILLS[@]}"; do
    dest="$dest_root/$skill"
    want="$(link_target_for "$dest_root" "$skill")"

    case "$MODE" in
      clean)
        if ours "$dest"; then
          [[ $DRY_RUN -eq 0 ]] && rm -rf "$dest"
          printf '%-22s %-28s %s\n' "$skill" "removed" "$dest"
        else
          printf '%-22s %-28s %s\n' "$skill" "skipped (not ours)" "$dest"
        fi
        ;;

      check)
        if [[ -L "$dest" && "$(readlink "$dest")" == "$want" ]]; then
          printf '%-22s %-28s %s\n' "$skill" "ok" "$dest"
        elif [[ -f "$dest/$MARKER" ]]; then
          if diff -rq "$CANON/$skill" "$dest" --exclude "$MARKER" >/dev/null 2>&1; then
            printf '%-22s %-28s %s\n' "$skill" "ok (copy)" "$dest"
          else
            printf '%-22s %-28s %s\n' "$skill" "DRIFT (copy differs)" "$dest"; status=1
          fi
        elif [[ -e "$dest" ]]; then
          printf '%-22s %-28s %s\n' "$skill" "DRIFT (unexpected)" "$dest"; status=1
        else
          printf '%-22s %-28s %s\n' "$skill" "MISSING" "$dest"; status=1
        fi
        ;;

      copy)
        if [[ -e "$dest" ]] && ! ours "$dest" && [[ $FORCE -eq 0 ]]; then
          printf '%-22s %-28s %s\n' "$skill" "REFUSED (real dir)" "$dest"; status=1; continue
        fi
        if [[ $DRY_RUN -eq 0 ]]; then
          rm -rf "$dest"; mkdir -p "$dest"
          cp -R "$CANON/$skill/." "$dest/"
          printf 'generated by tooling/scripts/sync-skills.sh --copy from %s\ndo not edit here\n' \
            "$CANON/$skill" > "$dest/$MARKER"
        fi
        printf '%-22s %-28s %s\n' "$skill" "copied" "$dest"
        ;;

      link)
        if [[ -L "$dest" && "$(readlink "$dest")" == "$want" ]]; then
          printf '%-22s %-28s %s\n' "$skill" "unchanged" "$dest"; continue
        fi
        if [[ -e "$dest" ]] && ! ours "$dest" && [[ $FORCE -eq 0 ]]; then
          printf '%-22s %-28s %s\n' "$skill" "REFUSED (real dir)" "$dest"; status=1; continue
        fi
        if [[ $DRY_RUN -eq 0 ]]; then
          rm -rf "$dest"
          ln -sfn "$want" "$dest"
        fi
        printf '%-22s %-28s %s\n' "$skill" "linked" "$dest"
        ;;
    esac
  done
done

echo
case "$MODE" in
  check) [[ $status -eq 0 ]] && note "$(plural ${#SKILLS[@]} skill), all destinations in sync." \
                            || note "Drift found. Run ./tooling/scripts/sync-skills.sh to fix." ;;
  clean) note "Cleaned." ;;
  *)     [[ $DRY_RUN -eq 1 ]] && note "Dry run: nothing was written." \
                              || note "$(plural ${#SKILLS[@]} skill) synced to $(plural ${#DESTS[@]} destination)." ;;
esac
exit $status
