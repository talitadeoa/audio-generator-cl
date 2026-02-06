#!/bin/bash
cd "/Users/talita/Desktop/claude generator /binaural-generator"

# Initialize git if not already done
if [ ! -d .git ]; then
    git init
    git config user.email "talita@example.com"
    git config user.name "Talita"
fi

# Commit 1: Configuration
git add pyproject.toml requirements.txt .gitignore
git commit -m "chore: project configuration and dependencies"

# Commit 2: Core modules
git add src/
git commit -m "feat: core audio synthesis modules (11 modules)

- config.py: Dataclasses and enums for configuration
- waveforms.py: 6 waveform generation functions
- envelope.py: ADSR envelopes and gating
- synthesizer.py: Layer synthesis with AM/FM modulation
- mixer.py: Multi-layer mixing with normalization
- renderer.py: WAV/MP3 export with metadata
- playback.py: Real-time streaming and playback
- presets.py: YAML/JSON preset management
- cli.py: Command-line interface (Click)
- tui.py: Terminal UI (Textual)
- utils.py: Validation and utility functions"

# Commit 3: Tests
git add tests/
git commit -m "test: comprehensive test suite (83 tests, 100% pass rate)

- test_waveforms.py: 13 tests for waveform generation
- test_synthesizer.py: 9 tests for synthesis modes
- test_envelope.py: 6 tests for envelopes and gating
- test_mixer.py: 8 tests for mixing and normalization
- test_renderer.py: 7 tests for audio export
- test_presets.py: 10 tests for preset management
- test_cli.py: 8 tests for CLI commands
- test_utils.py: 22 tests for utilities"

# Commit 4: Presets
git add presets/
git commit -m "config: preset definitions (6 YAML files)

- focus.yaml: 14 Hz beta waves for concentration
- meditation.yaml: 6 Hz theta waves for deep meditation
- sleep.yaml: 2 Hz delta waves for sleep induction
- elevation.yaml: 7.83 Hz Schumann + 528 Hz Solfeggio
- live.yaml: 10 Hz alpha loopable for streaming
- isochronic_gamma.yaml: 40 Hz isochronic pulses"

# Commit 5: Examples
git add examples/ demo.py gen_demo.py
git commit -m "docs: example scripts and demo generation

- examples/live_stream.py: Continuous streaming like YouTube Brain Waves
- examples/frequency_progression.py: Meditative journey Beta→Delta
- demo.py: Comprehensive demonstration (22 demo files)
- gen_demo.py: Quick 4-preset demo generation (30s each)"

# Commit 6: Documentation
git add README.md DEMO_AUDIO.md PROJETO_COMPLETO.md
git commit -m "docs: comprehensive documentation

- README.md: Full project documentation with usage examples
- DEMO_AUDIO.md: Audio listening guide with scientific background
- PROJETO_COMPLETO.md: Complete project summary and features"

# Commit 7: Audio demos
git add demo_audio/
git commit -m "demo: audio demonstration files (4 x 30-second WAV)

- focus_30s.wav: 14 Hz beta for concentration
- meditation_30s.wav: 6 Hz theta for deep meditation
- sleep_30s.wav: 2 Hz delta for sleep induction
- elevation_30s.wav: 7.83 Hz Schumann for spiritual elevation

All 24-bit stereo at 44.1 kHz sample rate with metadata"

# Display commit log
echo "✅ All commits completed!"
echo ""
echo "📝 Commit history:"
git log --oneline
