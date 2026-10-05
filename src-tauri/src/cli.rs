use clap::Parser;
use std::path::PathBuf;

#[derive(Parser, Debug, Clone, Default)]
#[command(name = "handy", about = "Handy - Speech to Text")]
#[command(group(clap::ArgGroup::new("recording_toggle")
    .args(["toggle_transcription", "toggle_post_process"])
    .multiple(true)))]
pub struct CliArgs {
    /// Start with the main window hidden
    #[arg(long)]
    pub start_hidden: bool,

    /// Disable the system tray icon
    #[arg(long)]
    pub no_tray: bool,

    /// Toggle transcription on/off (sent to running instance)
    #[arg(long)]
    pub toggle_transcription: bool,

    /// Toggle transcription with post-processing on/off (sent to running instance)
    #[arg(long)]
    pub toggle_post_process: bool,

    /// Use this microphone for the recording started by this toggle only
    #[arg(
        long,
        value_name = "NAME",
        requires = "recording_toggle",
        conflicts_with_all = ["cancel", "transcribe_file", "list_devices", "list_models"],
        value_parser = clap::builder::NonEmptyStringValueParser::new()
    )]
    pub microphone: Option<String>,

    /// Cancel the current operation (sent to running instance)
    #[arg(long)]
    pub cancel: bool,

    /// Enable debug mode with verbose logging
    #[arg(long)]
    pub debug: bool,

    /// Transcribe this WAV (16 kHz mono) headlessly and exit. Runs the same
    /// batch transcription path as the app — no mic, no VAD, no download
    /// (the model must already be installed).
    #[arg(short = 'f', long, value_name = "WAV")]
    pub transcribe_file: Option<PathBuf>,

    /// Model id to load for --transcribe-file (default: the selected model).
    #[arg(long)]
    pub model: Option<String>,

    /// Hard-select the compute device for --transcribe-file by its registry
    /// index (see --list-devices). Omit to use the persisted accelerator
    /// setting. transcribe-cpp (whisper-family) models only.
    #[arg(long, value_name = "N")]
    pub device_index: Option<usize>,

    /// List the transcribe-cpp compute devices (with indices) and exit.
    #[arg(long)]
    pub list_devices: bool,

    /// List the available models (with ids) and exit. Pass an id to --model.
    /// Honors --json for machine-readable output.
    #[arg(long)]
    pub list_models: bool,

    /// Repeat the transcription N times (best_ms reports the fastest run).
    #[arg(long, value_name = "N")]
    pub repeat: Option<usize>,

    /// Emit --transcribe-file results as JSON.
    #[arg(long)]
    pub json: bool,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn session_microphone_parses_forwarded_arguments() {
        for flag in ["--toggle-transcription", "--toggle-post-process"] {
            let args = CliArgs::try_parse_from(["handy", flag, "--microphone", "Wireless Mic Rx"])
                .unwrap();
            assert_eq!(args.microphone.as_deref(), Some("Wireless Mic Rx"));
        }
        let args = CliArgs::try_parse_from([
            "handy",
            "--toggle-transcription",
            "--microphone=Wireless Mic Rx",
        ])
        .unwrap();
        assert_eq!(args.microphone.as_deref(), Some("Wireless Mic Rx"));
    }

    #[test]
    fn session_microphone_requires_a_toggle_and_nonempty_name() {
        for args in [
            vec!["handy", "--microphone", "Wireless Mic Rx"],
            vec!["handy", "--cancel", "--microphone", "Wireless Mic Rx"],
            vec!["handy", "--toggle-transcription", "--microphone", ""],
            vec!["handy", "--toggle-transcription", "--microphone"],
            vec![
                "handy",
                "--toggle-transcription",
                "--microphone",
                "Wireless Mic Rx",
                "-f",
                "test.wav",
            ],
        ] {
            assert!(CliArgs::try_parse_from(args).is_err());
        }
        assert!(CliArgs::try_parse_from(["handy", "--toggle-transcription"])
            .unwrap()
            .microphone
            .is_none());
    }
}
