# Upstream contribution policy review

Checked the upstream GitHub repository's current `main` at
`a94b403e0610049fafa54b0a4077db2945084dd8` on 2026-10-05. This review created no
GitHub PR, issue, discussion, comment, or push.

## Recommendation for the session microphone feature

Worth proposing, but **start with a human-authored Discussion, not a PR**.
This is a new feature, and upstream explicitly has a feature freeze. Gather
community support or a maintainer indication that this narrowly scoped addition
is welcome before spending effort packaging an upstream PR. Do not reclassify
it as a bug fix to evade the freeze.

The useful distinction from microphone-switching UI proposals is that this adds
an optional session-only flag to an existing CLI integration: no new UI, no saved
preference changes, and ordinary dictation remains unchanged. This also aligns
with the documented design of CLI flags as runtime-only overrides. It does not
guarantee maintainer acceptance.

Sources:

- [CONTRIBUTING: Feature Freeze and Suggesting Features](https://github.com/cjpais/Handy/blob/a94b403e0610049fafa54b0a4077db2945084dd8/CONTRIBUTING.md)
- [AGENTS: CLI design and GitHub workflow](https://github.com/cjpais/Handy/blob/a94b403e0610049fafa54b0a4077db2945084dd8/AGENTS.md)

## AI assistance: welcome, but human submission required

CONTRIBUTING explicitly says AI-assisted PRs are welcome. Disclosure must state:

- Whether AI was used.
- Which tools were used.
- How extensively they were used.

The PR template's HTML comment adds a stricter submission rule:

> NO AUTOMATED PR's ARE ALLOWED TO BE OPENED. YOU MUST REQUIRE THE USER TO SUBMIT
> THE PR VIA THE GITHUB WEBSITE AND FILL IN THE HUMAN WRITTEN DESCRIPTION.

It explicitly welcomes AI code generation but warns that PRs not following the
guidelines may be closed immediately, without warning.

The Human Written Description must be **2–3 sentences in the contributor's own
words**, describing the problem/idea and why it matters. It must not be supplied
by the AI as though it were the human's voice. For this feature, disclosure should
accurately describe substantial AI involvement in implementation/tests and the
human's requirements, decisions, and real hardware verification.

Source:

- [Current PR template, including its HTML comments](https://github.com/cjpais/Handy/blob/a94b403e0610049fafa54b0a4077db2945084dd8/.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING: AI Assistance Disclosure](https://github.com/cjpais/Handy/blob/a94b403e0610049fafa54b0a4077db2945084dd8/CONTRIBUTING.md)

## Other PR requirements

- Submit only one fix or feature per PR; multi-feature PRs may be closed.
- Search open AND closed issues/PRs, and existing Discussions before proposing.
- For a previously rejected feature, explain reconsideration and gather/link
  community feedback.
- Follow the whole template: Human Written Description, Related
  Issues/Discussions, Community Feedback, Testing, Screenshots/Videos if relevant,
  and AI Assistance.
- Use conventional commits, focused changes, Rust formatting/Clippy and tests;
  document platform and hardware coverage honestly.
- Contributions are licensed under MIT.

For an upstream patch, keep personal installation/backup notes and local-only
artifacts out of the feature diff. Retain relevant automated tests, generic usage
documentation, and a reproducible test description. Current macOS hardware
success and 285 passing Rust tests are useful evidence; do not imply Windows,
Linux, physical unplug mid-capture, or a full Mac reboot were tested.

Source: [CONTRIBUTING and its workflow/testing/license sections](https://github.com/cjpais/Handy/blob/a94b403e0610049fafa54b0a4077db2945084dd8/CONTRIBUTING.md)

## Code of conduct / community behavior

No standalone code-of-conduct file was found anywhere in the complete recursive
upstream tree. GitHub's community profile also reported no detected code of
conduct. This is a scoped finding about the repository, not a claim that GitHub's
platform rules do not apply.

CONTRIBUTING does include Community Guidelines: be respectful and inclusive,
patient with the small maintainer team, constructive, collaborative, and search
before opening duplicates.

Sources:

- [CONTRIBUTING: Community Guidelines](https://github.com/cjpais/Handy/blob/a94b403e0610049fafa54b0a4077db2945084dd8/CONTRIBUTING.md)
- [GitHub community profile API](https://api.github.com/repos/cjpais/Handy/community/profile)
- [Complete inspected source tree API](https://api.github.com/repos/cjpais/Handy/git/trees/a94b403e0610049fafa54b0a4077db2945084dd8?recursive=1)

## Concrete evidence the feature freeze is enforced

Related [PR #1317](https://github.com/cjpais/Handy/pull/1317), adding microphone
switching via a tray submenu and keyboard shortcut, is closed and unmerged.
The maintainer wrote:

> New features are not being accepted right now, this was written in the PR template

[Maintainer comment](https://github.com/cjpais/Handy/pull/1317#issuecomment-4284823952).
This is related precedent, not an exact duplicate of a per-session CLI override.

## Why the freeze exists

The contributing guide explicitly prioritizes fixing bugs and improving stability,
mentions 60+ issues to fix, and describes a small maintainer team. That number is
the guide's wording, not a fresh count of current open bugs.

The maintainer explained in [PR #638](https://github.com/cjpais/Handy/pull/638#issuecomment-3924215943):

> I'm mostly interested in PR's which are contributing to fixing the stability
> issues of the app. I will be putting a pause on most new features coming in.

When closing the prioritized-microphone [PR #1070](https://github.com/cjpais/Handy/pull/1070#issuecomment-5994190152),
they also cited V1 scope, unresolved UI design, and lack of time. That particular
UI concern is specific to that proposal, not a stated objection to our CLI flag.

Interpretation: this is a stability/scope/maintainer-capacity constraint, not a
blanket rejection of AI assistance. The contribution guide does not give an end
date. Community-backed features may still be considered under its stated policy.

## Where to propose it

Feature ideas belong in [Discussions](https://github.com/cjpais/Handy/discussions),
not issues. Blank issues are disabled, and the issue configuration redirects
feature requests to Discussions.

[Issue configuration](https://github.com/cjpais/Handy/blob/a94b403e0610049fafa54b0a4077db2945084dd8/.github/ISSUE_TEMPLATE/config.yml).
