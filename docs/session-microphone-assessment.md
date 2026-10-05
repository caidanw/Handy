# Session-only microphone override: feasibility assessment

Assessed upstream checkout `a94b403` (package version 0.9.8) at `/Users/caidan/Projects/Handy`. This document records the initial source-inspection assessment. The feature has since been implemented and built; see [session-microphone-testing.md](session-microphone-testing.md) for current verification status. The installed Handy app and existing Karabiner mapping were not changed.

## Recommendation

Add an optional named microphone argument to the existing remote toggle:

```sh
handy --toggle-transcription --microphone "Wireless Mic Rx"
```

This was the proposed syntax. It is now supported by the built fork, but NOT by the unchanged official installed app.

- When idle, start using that device for this recording only.
- When recording the same binding, stop the existing recording; do not resolve or switch devices on the stop invocation.
- With no argument, use Handy's configured microphone/clamshell behavior as today. Set Handy's regular microphone to Default if normal dictation should follow the system default.
- Never change Handy's saved microphone preference or the macOS default input.
- If the explicit device is unavailable, report an error and remain idle rather than silently use another microphone.
- Preserve existing toggle ownership: CLI and keyboard plain-transcription triggers can stop each other's sessions. This feature need not introduce independent sessions or trigger-specific ownership.
- Require a running instance initially, matching the currently verified integration. Cold-start auto-recording is a separate behavior to decide and test.

## Existing path and likely changes

Paths below are relative to the repository root.

| File / location                                        | Current behavior                                                                 | Needed change                                                                                                                                                                                                      |
| ------------------------------------------------------ | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src-tauri/src/cli.rs`                                 | clap definitions; no microphone flag                                             | Optional string flag, restricted to recording toggle commands; parser tests.                                                                                                                                       |
| `src-tauri/src/lib.rs:854`                             | Single-instance callback scans argument strings for toggle flags                 | Parse forwarded arguments with the existing clap definition and forward the optional name. Must support normal clap quoting/`--microphone=...` forms rather than another fragile manual scan.                      |
| `src-tauri/src/signal_handle.rs`                       | Shared external-toggle helper for CLI/signals                                    | Pass the optional choice, or leave this helper unchanged and call a new coordinator entry point for CLI; signals continue to use no override.                                                                      |
| `src-tauri/src/transcription_coordinator.rs`           | Serial command queue, pure lifecycle decisions, deferred starts while processing | Carry the optional name on input, pending press, and Start effect. Stop does not apply a new name. Queued starts must retain their own metadata; rapid toggles must preserve existing remember/forget parity.      |
| `src-tauri/src/actions.rs:388,475`                     | Transcribe action prepares model/UI and calls `try_start_recording`              | Pass the accepted start's optional microphone into audio capture; reuse existing recording-error cleanup. Review the small ShortcutAction trait and its implementers rather than bypassing the normal action path. |
| `src-tauri/src/managers/audio.rs:474,637,816,983,1070` | Device resolution, stream reuse, start, stop, cancel                             | Resolve an explicit session device without persistent fallback; handle switching/releasing warm streams and cleanup on stop/cancel/start failure. Keep this behavior concentrated in the audio manager.            |

No frontend, settings schema, new dependency, custom IPC protocol, or background process is necessary. Existing single-instance transport already sends CLI arguments to the running app.

## Why it is not just a CLI flag

1. `start_microphone_stream` returns early if a healthy stream is already open. Always-on mode and the optional 30-second lazy close can therefore keep the previous microphone open. Passing a different name alone would not switch it.
2. Current missing-device fallback can persist `selected_microphone = None`. A session override needs a strict resolution path that does not use that persistence behavior.
3. Stop drains asynchronously; cancel can arrive while stopping. Device cleanup must follow actual capture completion and existing locking/generation rules, not an arbitrary timer.
4. Processing-time presses are remembered by `PendingPress`. A global temporary microphone variable would allow another trigger to overwrite the pending recording's choice. The name must travel with the request.
5. On-demand mode can simply close an overridden stream after capture and resolve regular settings on the next start. Always-on mode also needs to restore its regular warm stream after the override ends. Use current regular settings at restoration time rather than overwriting a concurrent preference change with a saved snapshot.
6. The explicit override should outrank clamshell routing for that session. Device names follow Handy's current selector semantics; duplicate names are an existing limitation. Stable CoreAudio IDs are a separate enhancement, not required for this DJI receiver.

## Verification scope

Extend the existing coordinator state-machine tests rather than introduce a new state machine:

- Start carries DJI selection; stop does not switch devices.
- Busy queued start retains DJI selection; two queued toggle presses cancel it.
- Cancel and failed start clear pending session metadata.
- Subsequent ordinary trigger carries no override.

Add parser coverage and a small testable audio-selection/stream-switch decision check covering override precedence, missing-device errors, and unchanged saved preference.

Hardware checks on this Mac:

1. Handy Default input with macOS default set to MacBook microphone: keyboard dictation captures MacBook.
2. DJI CLI/button start and stop captures Wireless Mic Rx; next keyboard session returns to MacBook.
3. Repeat with lazy-close and always-on modes, cancellation, rapid toggles, and unplugged DJI.
4. Confirm original settings file and macOS default input did not change; confirm normal Volume Up remains unaffected.
5. Test a rebuilt app's microphone/accessibility permissions and restart persistence.

## Effort and build constraints

Estimate: small-to-medium Rust change, roughly 5–6 production files plus tests/docs. A focused on-demand-only prototype is likely a few hours; a reliable patch covering warm streams, cancellation, queued triggers, and hardware tests is approximately 1–2 developer days. These are planning estimates, not measured implementation time.

Bun and Xcode are present. With user approval, Homebrew Rust/Cargo 1.99.0 and CMake 4.4.4 were installed; rustfmt and Clippy are available. `cargo metadata --manifest-path src-tauri/Cargo.toml --no-deps --format-version 1` successfully parsed Handy's manifest. Homebrew also installed/upgraded required dependencies. App dependencies have since been fetched, all 285 Rust tests passed, and an isolated release bundle was built. Hardware verification is pending the isolated app's permissions.

Local bundles use ad-hoc signing (`src-tauri/tauri.conf.json`). Installing a rebuilt app may require regranting Accessibility; BUILD.md documents this. Do not overwrite the working official app before testing a separately backed-up build. A build sharing the existing app identifier can also share Handy's settings and single-instance socket, so test isolation needs care.

Upstream is under a feature freeze. CONTRIBUTING.md requires feature discussion/community support before a feature PR. A local patch is feasible independently of whether upstream accepts it.
