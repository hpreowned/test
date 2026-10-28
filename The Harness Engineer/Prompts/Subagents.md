Create three subagents that review my Substack notes as a panel.

hook-reviewer: checks the first three lines only. Authority name in line one, hook family, does it match my note rules in CLAUDE.md.
conversion-reviewer: checks money only. Restack CTA, article bridge, paid signal.
claim-reviewer: checks facts only. Every number needs a source, every "I built" needs a real build. Flag anything unverified.

Each one returns approve or reject with reasons. None of them rewrite.

Then test the panel. Run all three on the note we wrote earlier and show me three separate verdicts.