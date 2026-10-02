// WORKED EXAMPLE — TypeScript / JavaScript. Copy to .dependency-cruiser.cjs at your repo root.
//
// The same contract as examples/python/importlinter.example.ini, expressed for a different
// parser. Read them side by side: the RULE is identical — api never reaches past service into
// repo, and background jobs never reach back up into api — and only the syntax differs.
//
// That is the whole point of the split between templates/ and examples/. The decision is
// portable; the executable is not. .github/skills/gates-draft/references/gates-by-stack.md
// holds the mapping, and gates-draft emits whichever of these your repo needs.

module.exports = {
  forbidden: [
    // --- The layering contract ---------------------------------------------------------
    // The equivalent of import-linter's [importlinter:contract:layers]. dependency-cruiser
    // has no single "layers" primitive, so a layered architecture is expressed as one
    // forbidden rule per illegal direction. Three layers means three rules, not one — worth
    // knowing before you assume this is a like-for-like port.
    {
      name: 'api-not-to-repo',
      severity: 'error',
      comment: 'Views ask the service layer. The service layer asks the repository.',
      from: { path: '^src/api' },
      to: { path: '^src/repo' },
    },
    {
      name: 'service-not-to-api',
      severity: 'error',
      comment: 'Layers point one direction only.',
      from: { path: '^src/service' },
      to: { path: '^src/api' },
    },
    {
      name: 'repo-not-upward',
      severity: 'error',
      comment: 'The innermost layer depends on nothing above it.',
      from: { path: '^src/repo' },
      to: { path: '^src/(api|service)' },
    },

    // --- The second contract, matching the Python file's `forbidden` block ---------------
    {
      name: 'tasks-not-to-api',
      severity: 'error',
      comment: 'Background jobs may call the service layer. They may not reach back into HTTP.',
      from: { path: '^src/tasks' },
      to: { path: '^src/api' },
    },

    // --- Public API surface (the ruff banned-api row of the table) -----------------------
    {
      name: 'no-deep-imports',
      severity: 'error',
      comment: 'Import a package by its entry point, not by reaching into its internals.',
      from: {},
      to: { path: 'node_modules/[^/]+/(?!package.json|index).*/' , dependencyTypes: ['npm'] },
    },

    // --- Housekeeping that has no import-linter equivalent -------------------------------
    { name: 'no-circular', severity: 'error', from: {}, to: { circular: true } },
    { name: 'no-orphans', severity: 'warn', from: { orphan: true, pathNot: '\\.d\\.ts$' }, to: {} },
  ],

  options: {
    doNotFollow: { path: 'node_modules' },
    tsPreCompilationDeps: true,
    tsConfig: { fileName: 'tsconfig.json' },

    // THE BASELINE. dependency-cruiser has no `ignore_imports` list and no equivalent of
    // import-linter's unmatched_ignore_imports_alerting, so the ratchet has to be built
    // differently: exclude the known-bad paths here, with a ticket, and shrink the list.
    //
    // Say this out loud when porting — the two tools are NOT feature-equivalent, and a
    // baseline that cannot expire is a permanent exemption with better paperwork. If the
    // ratchet matters to you, `depcruise --output-type err-long` in CI against a committed
    // known-violations count is the closest available substitute.
    exclude: {
      path: '^src/legacy/', // TODO(ARCH-118) retiring in Q4
    },
  },
};
