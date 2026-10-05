# Session microphone override: build and hardware test

## Implemented interface

```sh
handy --toggle-transcription --microphone "Wireless Mic Rx"
```

The name applies only to a new recording. A second plain-transcription toggle
stops the active session without applying its microphone argument. The same
option works with `--toggle-post-process`. Missing explicit devices fail instead
of using the default; no persisted input preference or OS input change is made.
Signals and keyboard shortcuts use the regular configured microphone.

## Verified so far

- 285 Rust library tests passed, including CLI parsing, queued microphone choices,
  stop behavior, cancellation, and failed-start metadata cleanup.
- Frontend build and ESLint passed.
- Rust formatting, changed Markdown/JSON formatting, and `git diff --check` passed.
- Repository-wide `bun run format:check` reports an unchanged upstream document:
  `docs/troubleshooting/ubuntu-26-04-gnome-wayland/README.md`. It was confirmed
  byte-identical to HEAD and left untouched.
- Clippy completed with upstream warnings in unchanged code.
- Isolated release app built and launched, with verified bundle identifier
  `com.pais.handy.session-test` and the new flag in `--help`.
- Real-device script passed in on-demand, lazy-close, and always-on modes:
  MacBook regular capture → DJI cancellation → DJI stop with an invalid name →
  missing-device error → regular capture. Always-on restoration passed after
  stop, cancellation, and failed start.
- Exact Default-input test passed: system-default AirPods → DJI override →
  AirPods again. App input preferences and macOS default remained unchanged.
- Each mode test followed a restart of the isolated app.
- Physical DJI Link-button speech test passed: logs show three complete DJI
  capture/start/stop/transcription cycles and History contains nonempty results.
  A second source-isolation retest also confirmed Wireless Mic Rx, not AirPods.
- Final physical-button test passed with Paste Method CtrlV: the user confirmed
  text appeared in a blank TextEdit document, and logs confirmed DJI capture,
  stop, transcription completion, CtrlV selection, and successful paste.
- The temporary physical-button mapping was restored exactly to its pre-test
  configuration; it again targets the official app.

## Checkout-only lifecycle cleanup (not yet deployed)

The later cleanup consolidates both startup failure stages into one rollback
path and isolates the stream-cleanup decisions for headless verification. Seven
new tests cover override close/restore, ordinary stream policy, open/start
failures, and successful readiness. The full checkout suite now passes **292**
tests. Controlled mutations disabling rollback and always-on restoration made
the relevant tests fail; both mutations were reverted before final validation.
Rust formatting, diff checks, and Clippy passed (existing upstream warnings only).

The installed app and permanent mapping were left unchanged by this cleanup;
the earlier deployed build's 285-test and hardware results above remain its record.
No upstream patch preparation or publishing was done.

## Isolated build

From the checkout root:

```sh
bun install --frozen-lockfile
CMAKE_POLICY_VERSION_MINIMUM=3.5 cargo test --manifest-path src-tauri/Cargo.toml --lib
CMAKE_POLICY_VERSION_MINIMUM=3.5 cargo clippy --manifest-path src-tauri/Cargo.toml --all-targets
CMAKE_POLICY_VERSION_MINIMUM=3.5 bun run tauri build --bundles app \
  --config "$PWD/scripts/tauri.session-test.json"
open "src-tauri/target/release/bundle/macos/Handy Session Test.app"
```

Use the RELEASE bundle. Upstream debug builds export `../src/bindings.ts` at
startup; opening a debug bundle normally can fail because that relative path is
not writable. No unrelated upstream fix was made.

The test app has separate settings/logs and a separate single-instance endpoint.
It is not installed over `/Applications/Handy.app`. The app is ad-hoc signed, so
macOS requires its own Microphone and Accessibility grants. A future rebuild may
require renewing its Accessibility grant; do not reset the official app's grants.

Prepared test-only settings live at:

- `~/Library/Application Support/com.pais.handy.session-test/settings_store.json`
- Logs: `~/Library/Logs/com.pais.handy.session-test/handy.log`

The test profile used **MacBook Pro Microphone** and **Default** during capture
checks. Its current regular input is **MacBook Pro Microphone** (preserved from
the user's test setting). Startup/update checks remain off and its shortcuts are
unique Ctrl+Shift+F19/F20. Paste Method is now CtrlV following the final paste test. It reuses the existing shared HF model cache without copying
private API settings. The official Handy settings and Karabiner mapping remain
unchanged.

## Automated capture checks

After granting permissions and getting past the test app's onboarding, set
**Paste Method to None** in the test app for this no-paste automated check:

```sh
python3 scripts/test-session-microphone.py
```

This check requires the isolated app already running. It starts/cancels regular
capture, starts/cancels DJI capture, stops DJI capture with an invalid microphone
name on the stop press, verifies that a missing microphone on a new start fails,
then verifies regular capture still works. It checks device names/audio
readiness in real app logs and confirms input preferences remain unchanged. It
never pastes speech.

Repeat after setting the TEST app to these modes:

1. Always-On off, lazy-close off.
2. Always-On off, lazy-close on (tests replacement of an idle warm stream).
3. Always-On on (tests restoring the regular warm stream after cancel/failure).

Do not edit a live settings file. Change modes through the test app's UI, or quit
that app before preparing its settings for a restart.

## Deployment and remaining optional coverage

- The production fork has now been installed at `/Applications/Handy.app`, with
  the previous app/settings/mapping backed up privately. The permanent DJI
  command includes `--microphone "Wireless Mic Rx"`; regular input is Default.
- Installed-app Default MacBook → DJI → Default MacBook capture/cancel check
  passed. Final physical-button paste smoke test was confirmed by the user and
  production logs. Deployment/rollback:
  `~/.config/karabiner/dji-handy-setup.md`.
- For mixed-input everyday use, set the deployed Handy app's regular microphone
  to Default; preserve its normal keyboard shortcut.
- Physical unplug/replug during capture, post-processing hardware behavior,
  ordinary physical-keyboard triggering, and a full Mac reboot have not been
  separately tested. Missing named-device failure, restoration, recording after
  app restarts, and the physical DJI dictation/paste path have been tested.

The permanent physical DJI mapping now targets the installed production fork
WITH `--microphone "Wireless Mic Rx"`. The isolated test app has been quit.

## Cleanup

Quit **Handy Session Test**, then remove its separate settings/logs directories if
no longer needed. Build artifacts are in `src-tauri/target/`. No custom daemon or
login item was installed for the test app.
