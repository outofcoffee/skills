---
name: shell-style
description: Apply the Google Shell Style Guide when creating or formatting shell scripts. Skip third-party scripts (e.g. Gradle wrapper, vendored tools).
---

When creating new shell scripts or modifying existing ones, follow the [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html).

**Do not modify third-party or generated shell scripts** — for example Gradle wrappers (`gradlew`), Maven wrappers (`mvnw`), vendored tool scripts, or any script whose header indicates it is auto-generated. If unsure whether a script is third-party, check for generator comments, licence headers from other projects, or whether it lives in a vendored/wrapper directory.

## When to use shell

- Shell is appropriate for small utilities, simple wrapper scripts, and task automation.
- If a script exceeds ~100 lines, needs complex data structures, or requires performance, recommend rewriting in another language.
- Bash is the only permitted shell scripting language. Use `#!/usr/bin/env bash`.
- Scripts must be compatible with both macOS (which ships Bash 3.2) and Linux. Avoid features introduced in Bash 4+ (e.g. associative arrays, `readarray`/`mapfile`, `${var,,}` case conversion, `|&` pipe shorthand) unless the project explicitly requires Bash 4+.

## File conventions

- Executables: use `.sh` extension or no extension.
- Libraries (sourced, not executed): must use `.sh` extension and should not be executable.
- SUID/SGID is forbidden — use `sudo` instead.
- Start every script with `set -euo pipefail` unless there is a specific reason not to.

## Formatting

- **Indentation**: 2 spaces. Never tabs (except in `<<-` here-documents).
- **Line length**: maximum 80 characters. Use here-documents or embedded newlines for longer strings.
- **Pipelines**: if a pipeline fits on one line, keep it on one line. Otherwise, split across lines with the pipe `|` at the start of each continuation line, indented by 2 spaces.
- **Control flow**: `; then` and `; do` go on the same line as `if`/`for`/`while`. `else`, `elif`, `fi`, `done` each get their own line.

```bash
if [[ -n "${my_var}" ]]; then
  do_something
else
  do_other
fi

for item in "${array[@]}"; do
  process "${item}"
done
```

- **Case statements**: indent alternatives by 2 spaces. Single-line actions may share a line with the pattern. Multi-line actions place pattern, body, and `;;` on separate lines. Avoid `;&` and `;;&`.

## Naming

- **Functions**: `lowercase_with_underscores`. Use `package::function` for namespaced libraries. Parentheses required after the name; opening brace on the same line.
- **Variables**: `lowercase_with_underscores`.
- **Constants and environment variables**: `UPPERCASE_WITH_UNDERSCORES`, declared near the top of the file. Use `readonly` or `export` as appropriate.
- **Local variables**: declare with `local`. When capturing command output, declare and assign on separate lines so `local` does not mask the return code:

```bash
local my_var
my_var="$(my_func)"
```

## Quoting and expansion

- **Quote all variables** unless intentionally allowing word splitting or glob expansion.
- Prefer `"${var}"` over `"$var"`.
- Use `"$@"` to pass arguments through; avoid `$*`.
- Use `$(command)` for command substitution — never backticks.
- Shell-internal integers (`$?`, `$#`, `$$`, `$!`) may optionally go unquoted.
- Use arrays and `"${array[@]}"` for safe handling of lists and command flags.

## Tests and conditionals

- Prefer `[[ … ]]` over `[ … ]` or `test`.
- Use `==` for string equality inside `[[ ]]`.
- Use `(( … ))` or `-lt`/`-gt`/`-eq` for numeric comparisons — never `<` or `>` inside `[[ ]]` for numbers.
- Use `-z` and `-n` for empty/non-empty string checks.
- Use `./*` instead of `*` to safely handle filenames starting with `-`.

## Arithmetic

- Use `(( … ))` or `$(( … ))` exclusively.
- Never use `let`, `$[ … ]`, or `expr`.

## Error handling

- Route all error messages to STDERR: `echo "Error: something failed" >&2`
- Always check return values — via `if`, `||`, or `$?`.
- Use `${PIPESTATUS[@]}` to check individual pipe segment return codes.

## Functions and comments

- **File header**: every script should have a brief comment describing its purpose.
- **Function comments**: every function that is not both obvious and short must have a comment block immediately before it. Library functions must always be documented. The comment block uses the following sections (omit any that do not apply):

```bash
#######################################
# Clean up files from the temp directory.
# Globals:
#   BACKUP_DIR
#   ORACLE_SID
# Arguments:
#   None
# Outputs:
#   Writes location of backup to stdout
# Returns:
#   0 if backup succeeded, non-zero on error
#######################################
cleanup() {
  …
}
```

- **TODO format**: `# TODO(identifier): description`
- Prefer functions over aliases in scripts.

## Built-ins over externals

- Prefer shell built-ins and parameter expansion over forking to `sed`, `awk`, or `expr` for simple operations.

## Pipes to while

- Avoid piping to `while` (creates a subshell). Use process substitution instead:

```bash
while read -r line; do
  process "${line}"
done < <(generate_lines)
```

## Miscellaneous

- Avoid `eval` entirely.
- No requirement to maintain POSIX compatibility — bashisms are fine.
