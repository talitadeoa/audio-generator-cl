#!/bin/bash

# Binaural Generator - Git Commits Script
# Execute: bash SETUP_GIT.sh

set -e

PROJECT_DIR="/Users/talita/Desktop/claude generator /binaural-generator"
cd "$PROJECT_DIR"

echo "🚀 Iniciando commits do Binaural Generator..."
echo ""

# Initialize git
if [ ! -d ".git" ]; then
    echo "📝 Inicializando repositório git..."
    git init
    git config user.email "talita@example.com"
    git config user.name "Talita"
    echo "✅ Git inicializado"
else
    echo "✅ Git já inicializado"
fi

echo ""
echo "📦 Fazendo commits estruturados..."
echo ""

# Commit 1
echo "Commit 1: Configuração"
git add pyproject.toml requirements.txt .gitignore 2>/dev/null || true
git commit -m "chore: project configuration and dependencies" 2>/dev/null || echo "  (pulado - não há mudanças)"
echo ""

# Commit 2
echo "Commit 2: Módulos Core"
git add src/ 2>/dev/null || true
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
- utils.py: Validation and utility functions" 2>/dev/null || echo "  (pulado)"
echo ""

# Commit 3
echo "Commit 3: Testes"
git add tests/ 2>/dev/null || true
git commit -m "test: comprehensive test suite (83 tests, 100% pass rate)

- test_waveforms.py: 13 tests for waveform generation
- test_synthesizer.py: 9 tests for synthesis modes
- test_envelope.py: 6 tests for envelopes and gating
- test_mixer.py: 8 tests for mixing and normalization
- test_renderer.py: 7 tests for audio export
- test_presets.py: 10 tests for preset management
- test_cli.py: 8 tests for CLI commands
- test_utils.py: 22 tests for utilities" 2>/dev/null || echo "  (pulado)"
echo ""

# Commit 4
echo "Commit 4: Presets"
git add presets/ 2>/dev/null || true
git commit -m "config: preset definitions (6 YAML files)

- focus.yaml: 14 Hz beta waves for concentration
- meditation.yaml: 6 Hz theta waves for deep meditation
- sleep.yaml: 2 Hz delta waves for sleep induction
- elevation.yaml: 7.83 Hz Schumann + 528 Hz Solfeggio
- live.yaml: 10 Hz alpha loopable for streaming
- isochronic_gamma.yaml: 40 Hz isochronic pulses" 2>/dev/null || echo "  (pulado)"
echo ""

# Commit 5
echo "Commit 5: Exemplos"
git add examples/ demo.py gen_demo.py 2>/dev/null || true
git commit -m "docs: example scripts and demo generation

- examples/live_stream.py: Continuous streaming like YouTube Brain Waves
- examples/frequency_progression.py: Meditative journey Beta→Delta
- demo.py: Comprehensive demonstration (22 demo files)
- gen_demo.py: Quick 4-preset demo generation (30s each)" 2>/dev/null || echo "  (pulado)"
echo ""

# Commit 6
echo "Commit 6: Documentação"
git add README.md DEMO_AUDIO.md PROJETO_COMPLETO.md 2>/dev/null || true
git commit -m "docs: comprehensive documentation

- README.md: Full project documentation with usage examples
- DEMO_AUDIO.md: Audio listening guide with scientific background
- PROJETO_COMPLETO.md: Complete project summary and features" 2>/dev/null || echo "  (pulado)"
echo ""

# Commit 7
echo "Commit 7: Demos de Áudio"
git add demo_audio/ 2>/dev/null || true
git commit -m "demo: audio demonstration files (4 x 30-second WAV)

- focus_30s.wav: 14 Hz beta for concentration
- meditation_30s.wav: 6 Hz theta for deep meditation
- sleep_30s.wav: 2 Hz delta for sleep induction
- elevation_30s.wav: 7.83 Hz Schumann for spiritual elevation

All 24-bit stereo at 44.1 kHz sample rate with metadata" 2>/dev/null || echo "  (pulado)"
echo ""

# Display results
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ COMMITS COMPLETADOS!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Histórico de commits:"
git log --oneline | head -10
echo ""
echo "📊 Status:"
git status
echo ""
echo "🎯 Próximos passos:"
echo "  1. git log --all (para ver todos os commits)"
echo "  2. git tag -a v1.0.0 -m 'Release v1.0.0' (para marcar versão)"
echo "  3. git remote add origin <URL> (para conectar repositório remoto)"
echo "  4. git push -u origin main (para fazer push)"
