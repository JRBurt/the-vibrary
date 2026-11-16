# Skill: Code Review

When reviewing a change, check correctness first, then simplification
opportunities, then efficiency. Flag only issues you can point to a concrete
failure scenario for: a specific input, state, or sequence of calls that
produces a wrong result or a crash. A stylistic preference is not a finding.

Favor fewer, higher-confidence findings over an exhaustive list. A review that
reports ten speculative issues is less useful than one that reports two real
bugs with a clear repro.
