"""Shadow-mode harness for TypeSafe Jev opportunity specs.

Loads an opportunity spec, lints it against the repo's anti-patterns, asks Jev the spec's
questions about each fixture, turns answers into Act | Review | Escalate bands, and writes a
log plus a Markdown report. It never takes an action on anything.
"""

__version__ = "0.1.0"
