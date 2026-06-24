# Git hooks — Source Onboarding gotcha

`commit-msg` enforces the **Source Onboarding Protocol** (CLAUDE.md §16 / DATA_BUILDING_BLOCKS
B1a): it blocks a commit that adds/links a new media/data source (a feed URL, a new collector,
or a `COLLECTOR_EXPECTATIONS` entry in the `transfer/*` collector files) unless the commit
message contains the marker `[source-onboarded]` — which asserts all 5 gates passed
(TYPE → ENGINE → FORMAT → CURRENCY+ACCESS → TEST→LINK→DEPLOY).

## Install (once per clone)

```
git config core.hooksPath .githooks
```

That's it — hooks here are version-controlled (and `.gitattributes` forces LF so the bash
script parses correctly after a Windows checkout). To add a legitimate source: pass the 5
gates, then put `[source-onboarded]` in your commit message.
