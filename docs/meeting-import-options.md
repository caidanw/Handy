# DJI onboard recordings: existing apps vs a small independent importer

Research checked 2026-10-05. No application was installed or built for this
investigation; existing-app findings are based on primary docs, licenses,
release assets, and selected source code. No changes to the working Handy setup.

## Required experience

Open app → connect the DJI Mic 2 TRANSMITTER directly via USB-C → click Import
→ copy new recordings, convert automatically, transcribe, and show results.

The Mobile Receiver is the USB audio/HID device used for live dictation, not the
connection DJI documents for exporting onboard recordings. Long recordings are
split into multiple WAV files. The actual transmitter volume layout and naming
must be inspected before implementing reliable device detection/session grouping.

[DJI FAQ](https://www.dji.com/mic-2/faq).

## Verified open-source options

| App                         | License / scope                                                             | Relevant verified capabilities                                                                                                                                                                                         | Main gap for this workflow                                                                                                                                                                                              |
| --------------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Muesli                      | MIT                                                                         | Native macOS app; released v0.8.4 import pipeline converts m4a/mp4/wav/mp3, transcribes, optionally diarizes, generates title/summary, and saves a meeting. Local transcription; local Ollama or hosted summaries.     | Released picker allows ONE file. No documented DJI mount detection or automatic assembly of transmitter segments.                                                                                                       |
| Vibe                        | MIT                                                                         | macOS app releases; local audio/video transcription, batch files, multiple transcript export formats. Current README also documents local Ollama analysis/batch summaries and speaker diarization.                     | Batch file input is not the same as detecting a DJI transmitter and importing only new device recordings. Advanced capabilities in current main should be verified in the chosen release.                               |
| Meetily Community           | MIT community app                                                           | Official project ships Apple Silicon macOS DMG; local Whisper/Parakeet; existing-audio import is documented as Beta; summaries can use local Ollama or hosted providers.                                               | General file import rather than a verified one-button device importer. PRO is a separate offering; don't assume its extras are in the open-source community edition.                                                    |
| Buzz                        | MIT                                                                         | macOS releases; local audio/video file import, queued transcription, TXT/SRT/VTT export. Project docs describe watch-folder automation.                                                                                | Primarily a transcription workflow rather than a Granola-like meeting knowledge library; watched folders don't solve device copying/session grouping by themselves.                                                     |
| Anarlog (formerly Hyprnote) | MIT community app; enterprise components have a separate commercial license | Explicit open-source Granola alternative; local notes/SQLite, selectable local transcription and local LLM summaries/chat. Official offline guide verifies MP3 import and local transcription/summary in a short test. | Must configure transcription AND intelligence as local independently. The team also builds a different app called Char; don't confuse that codebase/license with this community app. No verified DJI-specific importer. |

All five have macOS release assets. "Open source" here describes the application
code; model weights and optional providers have their own licenses and terms.
No claim is made that all summarization configurations are offline, or that all
current-main features are present in every downloadable release.

### Sources

- [Muesli repo / MIT license / release downloads](https://github.com/Muesli-HQ/muesli)
- [Muesli released import implementation](https://github.com/Muesli-HQ/muesli/blob/v0.8.4/native/MuesliNative/Sources/MuesliNativeApp/AudioFileImportController.swift): `allowsMultipleSelection = false`; conversion and complete import pipeline are explicit in source.
- [Vibe repo / MIT / features](https://github.com/thewh1teagle/vibe)
- [Vibe v3.2.2 macOS releases](https://github.com/thewh1teagle/vibe/releases/tag/v3.2.2)
- [Canonical Meetily repo / community-vs-PRO scope](https://github.com/Zackriya-Solutions/meetily)
- [Meetily audio import docs](https://docs.meetily.ai/features/audio-import): decoding/conversion, background jobs and supported formats; each imported file becomes a meeting.
- [Buzz repo / MIT](https://github.com/chidiwilliams/buzz)
- [Buzz file import UI](https://chidiwilliams.github.io/buzz/docs/usage/file_import)
- [Anarlog canonical repo / license boundaries](https://github.com/fastrepl/anarlog)
- [Anarlog's disclosed offline test](https://anarlog.so/blog/offline-meeting-transcription-mac/): short synthetic sample, not proof of long-meeting accuracy; their own accuracy check found errors in numbers/ownership/deadlines.

Search results initially surfaced a similarly named Meetily fork. The canonical
project was verified through GitHub redirects from Zackriya-Solutions/meeting-minutes
to Zackriya-Solutions/meetily; recommendations refer to that canonical project.

## Direct transcribe.cpp feasibility

[transcribe.cpp](https://github.com/handy-computer/transcribe.cpp) is independent
of Handy: an MIT C/C++ GGUF speech inference engine, with Metal enabled on Apple
Silicon and a `transcribe-cli` executable. Its README specifies 16 kHz mono WAV
input. Latest published engine release checked: v0.3.1, including a native macOS
ARM64 Metal package. The CLI may still need building; a native-library archive is
not automatically a finished GUI or a bundled CLI application.

We can reuse a compatible already-downloaded GGUF model without invoking Handy,
but must test compatibility with the pinned engine build. The engine is not a
meeting-notes UI or a general summarizing LLM. Timestamps and speaker labels are
model-dependent; a separate diarization model/pipeline may be required. Treat
speaker identification as a separate design choice, not a free consequence of
transcription.

## Three approaches

1. **Use an existing app.** Lowest maintenance. Trial Muesli for meeting notes and
   Vibe for multi-file import. They already avoid manual conversion commands.
   Expect file selection/drag-and-drop rather than a verified DJI-specific button.
2. **Thin device importer feeding an existing app.** Copy/deduplicate recordings
   with a tiny UI, then use an app's supported CLI/import interface. Muesli has a
   file-transcription CLI, but GUI import capabilities (such as diarization) must
   not be assumed to exist identically in the CLI. This still has two moving
   applications to maintain.
3. **Small standalone native importer using transcribe.cpp.** Best exact fit for
   the non-negotiable one-button device workflow; more engineering/maintenance
   than installing an existing app, but independent of Handy and upstream freezes.

For option 3, keep the first version narrow:

- One SwiftUI window: device status, **Import new recordings**, progress, results.
- Detect the known mounted transmitter while the app is open. A one-time device
  selection may be needed before safe recognition; do not scan arbitrary volumes.
- Copy source WAVs locally before processing; verify copies and never auto-delete
  transmitter recordings. Mark completed imports so reconnecting doesn't duplicate
  them; don't mark partial copies/transcription failures as finished.
- Convert automatically using native macOS audio facilities for DJI WAV files.
  Keep 24-bit/32-bit-float originals; don't sacrifice recoverable peaks during
  conversion. FFmpeg can remain an alternative if broader input formats are needed.
- Process files sequentially with a pinned bundled transcribe.cpp engine and an
  appropriate local model. Handle long files in tested chunks and preserve timing.
- Group recording parts only where actual session metadata supports it; don't
  merge unrelated meetings merely because they were imported together.
- Save portable transcripts plus recording/part references. Plain files/local
  search are sufficient initially; no web backend, vector database, account, or
  always-running daemon is necessary.
- Add summary/action-item extraction only after choosing a local vs hosted LLM
  policy. Keep the raw transcript, distinguish inferences from quotes, and make
  it possible to verify names/numbers/decisions against the audio.

One-time model setup is unavoidable for offline inference. After setup, routine
import should be one button with no terminal commands, model picker, or manual
conversion step. Automatic processing does not mean AI notes can be trusted
without review.

## Local-first direction clarified

The user wants local transcription and local model summaries, with an optional
explicit cloud-summary mode using a Codex subscription if supported. They are
open to a small fork or a new app, but no implementation target is approved yet.

Local checks found an Apple M5 Max with 128 GB RAM, a running Ollama service, and
an installed `gemma4:e2b` model. This avoids needing a new local inference server
for a first prototype. Benchmark that model on a harmless representative meeting
before promising summary quality or selecting a larger replacement. Long-meeting
summaries need context-aware chunking; owners/dates must not be invented.

Codex CLI 0.159.3 is installed and reports ChatGPT login. Official documentation
supports `codex exec` for non-interactive scripts, piped input and final output,
and reuses saved CLI authentication. ChatGPT sign-in provides subscription
access; API-key use is separately billed. OpenAI recommends API keys for general
programmatic/CI automation, so a personal desktop option should use the user's
installed/signed-in official CLI, not repurpose or copy authentication tokens.
Subscription/workspace eligibility and rate limits still apply.

Sources:

- [Codex authentication](https://developers.openai.com/codex/auth)
- [Codex non-interactive mode](https://developers.openai.com/codex/noninteractive)
- [Codex configuration reference](https://developers.openai.com/codex/config-reference)

A cloud mode must be explicitly selected and clearly indicate that transcript
text leaves the Mac. Never silently fall back from local to cloud. Use a restricted
text-summary invocation without shell/web/MCP tools, ignore unrelated user/project
configuration, and do not treat transcript content as executable instructions.
The installed CLI supports `--ignore-user-config`, `--ephemeral`, restricted
sandbox mode and output capture; confirm tool-disable settings before implementing.
Ephemeral mode avoids local session files, not provider-side retention.

Recommended small-app direction: SwiftUI importer + transcribe.cpp + the existing
Ollama runtime; optional Codex CLI summary provider later. Avoid reimplementing
a full meeting suite. A Muesli fork becomes more attractive if diarization,
speaker-labelled meeting history and rich editing are needed immediately, since
its released import pipeline already supplies them. Vibe is an alternative if
batch transcription matters more than meeting-note UX.

## CLI + Shortcuts alternative

Speaker labels are required, but the user now prefers investigating a CLI/simple
program with Apple Shortcuts rather than carrying a full desktop application.
This is likely a better minimal fit: Shortcut as the front end, one importer
executable handling reliable file processing.

On the actual Mac (26.7.1), `man launchd.plist` documents `StartOnMount`: a job
starts whenever a filesystem mounts. A user LaunchAgent can therefore invoke a
short-lived importer (or `shortcuts run`) and exit; no custom always-running
watcher is necessary. The job must filter the enrolled transmitter volume before
reading recordings. It wakes on ALL mounts, not only DJI mounts. Apple's current
Shortcuts automation docs do not list volume attachment as a trigger, so do not
assume Shortcuts alone supplies it on this Mac. A manual Shortcut is also a useful
first-stage fallback before automatic mount processing is enabled.

[Apple Shortcuts CLI documentation](https://support.apple.com/guide/shortcuts-mac/run-shortcuts-from-the-command-line-apd455c82f02/mac)
confirms `shortcuts run`, file input/output arguments and exit status. Avoid
interactive prompts in the automatically launched pipeline; initial macOS file
access approval/setup may still require an attended first run.

For an Apple-Silicon-only CLI, [FluidAudio](https://github.com/FluidInference/FluidAudio)
is an Apache-2.0 Swift SDK supporting both local ASR and offline diarization.
Its [CLI docs](https://github.com/FluidInference/FluidAudio/blob/main/Documentation/CLI.md)
include file `transcribe` and offline diarization `process` commands. This is the
SDK used by Muesli, so we may reuse the inference capability without forking its
whole app. A single Swift CLI using its SDK and native audio conversion could
be simpler than transcribe.cpp PLUS a second diarization runtime. transcribe.cpp
remains an alternative transcription backend if a benchmark favors it.

Recommended pipeline: recognize enrolled transmitter → copy/deduplicate WAVs →
identify same-session parts → normalize → local ASR + diarization → align speaker
segments with transcript timings → local Ollama summary → save portable results.
Speaker1/2 labels are automatic; names require a per-meeting mapping, editable
later through a file or optional second Shortcut. Do not infer names from voice.

Output can be ordinary meeting folders containing originals, speaker-tagged
transcript text/JSON, speaker-name mapping and Markdown notes. No custom UI,
account, vector database or new web backend is needed. Preserve/resume successful
stages on reconnect/retry; never delete originals automatically. An interrupted
copy or uncertain session grouping must not be treated as a completed import.

No fork, CLI implementation or launch automation has been installed yet.
Actual transmitter volume identity and recording layout still need inspection.

## FluidAudio vs transcribe.cpp

Both can be used without Handy or Muesli, and both now support speech recognition
and diarization. Earlier suggestions that transcribe.cpp necessarily needs a
second inference engine for speaker detection were too strong: its current
catalog includes Sortformer diarization and joint speaker-aware ASR families.
A diarization-only model still requires aligning its speaker segments with ASR
word/segment timings; that integration is not automatic merely because both
models run in one library.

| Dimension                | FluidAudio                                                                        | transcribe.cpp                                                                            |
| ------------------------ | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Primary interface        | Swift SDK / Swift CLI                                                             | C/C++ C API / CLI; wrappers such as Rust                                                  |
| Platforms                | Apple-focused (macOS/iOS)                                                         | Portable CPU/GPU runtime; macOS, Windows, Linux                                           |
| Acceleration             | Core ML; many paths target ANE, some pipelines use CPU/other Core ML placements   | ggml; Metal on Apple Silicon, CPU, Vulkan, CUDA                                           |
| Models                   | Core ML bundles; broad audio SDK including ASR, diarization, VAD                  | GGUF speech models; multiple ASR families and dedicated/joint diarization models          |
| Offline speaker workflow | Documented full-file segmentation/embeddings/VBx clustering pipeline              | Sortformer plus joint ASR/diarization models; workflow/caps depend on chosen model        |
| Long files               | Documented disk-backed ASR chunking/merging and memory-mapped offline diarization | Support and operating-point choices depend on model family; validate chosen file pipeline |
| Existing cached models   | Cannot directly load the current Handy GGUF; download compatible Core ML bundles  | Compatible existing GGUF can be reused, after checking engine/model compatibility         |
| Code license             | Apache-2.0                                                                        | MIT                                                                                       |

The transcribe.cpp Sortformer model is limited to four speaker slots, but this
is that model's limit, not a universal limit of the runtime. FluidAudio also has
a four-speaker Sortformer option; its offline VBx clustering is a different
pipeline. Quiet speech, overlap, similar voices and cross-part label continuity
need real recording tests for either choice.

No universal accuracy/speed winner is established by comparing project marketing
benchmarks. Exact models, quantization, hardware and audio differ. On this M5 Max,
both runtimes are plausible. FluidAudio may reduce Swift/macOS integration work;
transcribe.cpp has portability and existing-cache advantages. Neither provides
LLM meeting summaries; keep Ollama/Codex as a separate summary step.

Sources:

- [FluidAudio](https://github.com/FluidInference/FluidAudio)
- [FluidAudio offline diarization](https://github.com/FluidInference/FluidAudio/blob/main/Documentation/Diarization/GettingStarted.md)
- [FluidAudio long transcription](https://github.com/FluidInference/FluidAudio/blob/main/Documentation/ASR/LongTranscription.md)
- [transcribe.cpp model catalog](https://github.com/handy-computer/transcribe.cpp)
- [transcribe.cpp Sortformer model limits](https://github.com/handy-computer/transcribe.cpp/blob/main/docs/models/diar_streaming_sortformer_4spk-v2.1.md)

Recommended next evaluation: a representative DJI recording with two or more
speakers, comparing transcript accuracy, speaker errors/continuity, quiet speech,
processing time and memory. A short sample verifies the pipeline; a longer sample
is needed before claiming meeting-length reliability.
