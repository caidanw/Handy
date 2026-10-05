#!/usr/bin/env python3
"""Hardware check for the isolated Handy Session Test app; never pastes speech.

Start that app and grant permissions first. Its regular microphone (configured
or system default) must differ from DJI. Repeat with all stream modes.
"""
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "src-tauri/target/release/bundle/macos/Handy Session Test.app/Contents/MacOS/handy"
DATA = Path.home() / "Library/Application Support/com.pais.handy.session-test"
LOG = Path.home() / "Library/Logs/com.pais.handy.session-test/handy.log"
OVERRIDE = "Wireless Mic Rx"


def settings():
    return json.loads((DATA / "settings_store.json").read_text())["settings"]


def default_microphone_name():
    devices = json.loads(subprocess.check_output(
        ["system_profiler", "SPAudioDataType", "-json"], text=True, timeout=15
    ))
    names = [device["_name"] for group in devices["SPAudioDataType"]
             for device in group.get("_items", [])
             if device.get("coreaudio_default_audio_input_device") == "spaudio_yes"]
    assert len(names) == 1, "Could not identify the system default input"
    return names[0]


def command(*args):
    subprocess.run([str(EXE), *args], check=True, timeout=15, capture_output=True)


def tail(offset):
    with LOG.open("rb") as stream:
        stream.seek(offset)
        return stream.read().decode("utf-8", errors="replace")


def wait_for(offset, marker):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        text = tail(offset)
        if marker in text:
            return text
        time.sleep(0.1)
    raise AssertionError(f"Timed out waiting for {marker!r}; inspect {LOG}")


def capture_and_cancel(microphone=None):
    offset = LOG.stat().st_size
    args = ["--toggle-transcription"]
    if microphone:
        args.extend(["--microphone", microphone])
    command(*args)
    text = wait_for(offset, "recording is ready")
    assert "Recording requested for binding transcribe" in text
    if microphone:
        assert f'Using device: Ok("{microphone}")' in text
    command("--cancel")
    return wait_for(offset, "Operation cancellation completed - returned to idle state")


def capture_and_stop(microphone):
    offset = LOG.stat().st_size
    command("--toggle-transcription", "--microphone", microphone)
    started = wait_for(offset, "recording is ready")
    assert f'Using device: Ok("{microphone}")' in started
    # The stop invocation must not resolve this deliberately missing name.
    command("--toggle-transcription", "--microphone", "handy-test-missing-on-stop")
    wait_for(offset, "Recording stopped and samples retrieved")
    stopped = wait_for(offset, "busy=false")
    assert "TranscribeAction::stop called" in stopped
    assert "Requested microphone 'handy-test-missing-on-stop'" not in stopped
    return stopped


def main():
    assert EXE.is_file(), "Build the isolated release bundle first"
    assert LOG.is_file(), "Start Handy Session Test and grant permissions first"
    # Never let a missing test instance become an accidental cold launch.
    processes = subprocess.check_output(["ps", "-axo", "command="], text=True).splitlines()
    assert any(p.strip().startswith(str(EXE)) for p in processes), "Test app is not running"
    initial = settings()
    default_input = default_microphone_name()
    regular = initial["selected_microphone"] or default_input
    assert regular != OVERRIDE, "Regular input must differ from DJI for this test"
    assert not initial.get("clamshell_microphone"), "Disable clamshell override for this check"
    assert initial["paste_method"] == "none", "Use Paste Method: None in the test app"
    try:
        first = capture_and_cancel()
        if not initial["always_on_microphone"]:
            assert f'Using device: Ok("{regular}")' in first
        overridden = capture_and_cancel(OVERRIDE)
        if initial["always_on_microphone"]:
            assert f'Using device: Ok("{regular}")' in overridden, "Regular warm stream not restored"

        stopped = capture_and_stop(OVERRIDE)
        if initial["always_on_microphone"]:
            assert f'Using device: Ok("{regular}")' in stopped, "Regular warm stream not restored after stop"

        offset = LOG.stat().st_size
        command("--toggle-transcription", "--microphone", "handy-test-missing-microphone")
        wait_for(offset, "Requested microphone 'handy-test-missing-microphone' is unavailable")
        failed = wait_for(offset, "did not begin recording; staying idle")
        assert "Recording requested for binding" not in failed, "Missing device silently fell back"
        if initial["always_on_microphone"]:
            assert f'Using device: Ok("{regular}")' in failed, "Regular warm stream not restored after failure"

        final = capture_and_cancel()
        if not initial["always_on_microphone"]:
            assert f'Using device: Ok("{regular}")' in final, "Session override leaked"
        current = settings()
        for key in ["selected_microphone", "clamshell_microphone", "always_on_microphone", "lazy_stream_close"]:
            assert current.get(key) == initial.get(key), f"Setting changed: {key}"
        assert default_microphone_name() == default_input, "System default input changed during test"
        print(f"PASS: {regular} → DJI cancel → DJI stop → missing-device error → regular; app and OS input settings unchanged")
    finally:
        command("--cancel")


if __name__ == "__main__":
    main()
