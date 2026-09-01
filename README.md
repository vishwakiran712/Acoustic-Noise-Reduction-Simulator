# 🔇 Acoustic Noise Reduction Simulator

> An interactive acoustic DSP laboratory for simulating noise-corrupted signals, applying digital noise-reduction techniques, and quantitatively evaluating signal recovery performance.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green?logo=qt)
[![NumPy](https://img.shields.io/badge/Numerical-NumPy-orange?logo=numpy)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/Signal%20Processing-SciPy-blue?logo=scipy)](https://scipy.org/)
[![Matplotlib](https://img.shields.io/badge/Visualization-Matplotlib-orange?logo=matplotlib)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<img width="938" height="496" alt="image" src="https://github.com/user-attachments/assets/efe4b9a5-fa9d-4e18-8af3-3dfa3e274a65" />


---

## 📌 Overview

**Acoustic Noise Reduction Simulator** is an interactive desktop application for studying how digital signal-processing techniques can recover an acoustic signal corrupted by different types of noise.

The simulator creates a clean acoustic signal, introduces a selectable noise environment at a controlled target SNR, applies a configurable recovery filter, and quantitatively compares the recovered signal against the original clean signal.

The application combines:

* Acoustic signal synthesis
* Realistic noise modeling
* Target-SNR calibration
* Digital filtering
* Time-domain analysis
* FFT spectral analysis
* SNR evaluation
* RMSE analysis
* Cross-correlation
* Automated engineering assessment

This makes it useful as a practical laboratory for **acoustics, DSP, signal conditioning, noise reduction, and acoustic instrumentation**.

---

# ✨ Key Features

## 🎵 Acoustic Signal Generator

The simulator generates a clean sinusoidal acoustic signal:

```text
x(t) = A · sin(2πft)
```

The signal frequency can be configured from:

```text
20 Hz → 2000 Hz
```

and amplitude from:

```text
0.1 → 5.0
```

The default signal is:

```text
Frequency = 220 Hz
Amplitude = 1.0
```

The generated clean signal acts as the ground truth for evaluating the effectiveness of the noise-reduction process.

---

# 🌪️ Noise Environment Simulation

The application supports six different noise environments:

| Noise Type                        | Description                                              |
| --------------------------------- | -------------------------------------------------------- |
| **Gaussian Noise**                | Normally distributed random noise                        |
| **White Noise**                   | Uniform broadband random noise                           |
| **Low-Frequency Rumble**          | Low-frequency noise generated through low-pass filtering |
| **50 Hz Electrical Interference** | Power-line interference with harmonic content            |
| **60 Hz Electrical Interference** | 60 Hz power-line interference with harmonic content      |
| **Random Impulse Noise**          | Sparse high-amplitude impulsive disturbances             |

These models allow the same acoustic signal to be tested against fundamentally different noise characteristics.

---

# ⚡ Electrical Interference Modeling

The simulator specifically models common power-line interference.

### 50 Hz Interference

```text
n(t) = A[
sin(2π50t)
+ 0.3 sin(2π150t)
]
```

### 60 Hz Interference

```text
n(t) = A[
sin(2π60t)
+ 0.3 sin(2π180t)
]
```

This provides a useful laboratory example of **periodic electromagnetic/electrical interference contaminating acoustic measurements**.

---

# 💥 Impulse Noise Modeling

Random impulse noise is simulated as sparse, high-amplitude spikes.

Approximately:

```text
1.5% of samples
```

are randomly selected and assigned positive or negative impulses.

This provides a simple model for impulsive disturbances that can occur in practical measurement systems.

---

# 🎯 Target SNR Calibration

Instead of relying only on an arbitrary noise amplitude, the simulator allows the user to specify a **target SNR**.

The target SNR range is:

```text
-10 dB → +30 dB
```

The application automatically scales the generated noise to achieve the selected target SNR.

Conceptually:

```text
Clean Signal
     │
     ▼
Calculate Signal Power
     │
     ▼
Select Target SNR
     │
     ▼
Calculate Required Noise Power
     │
     ▼
Scale Noise
     │
     ▼
Noise-Corrupted Signal
```

This makes experiments reproducible and allows controlled comparisons between different noise environments.

---

# 🧮 SNR Calculation

The simulator evaluates signal-to-noise ratio using:

```text
SNR = 10 log₁₀(Psignal / Pnoise)
```

It calculates SNR both **before and after noise reduction**.

The improvement is:

```text
ΔSNR = SNRafter − SNRbefore
```

This provides a direct quantitative measure of whether the selected filtering strategy actually improved signal quality.

---

# 🎚️ Noise Reduction Methods

The application provides four recovery strategies.

## 1. Low-Pass Filtering

A fourth-order Butterworth low-pass filter is applied using zero-phase filtering.

```text
Input
  │
  ▼
Butterworth LPF
  │
  ▼
Recovered Signal
```

This is useful for suppressing high-frequency noise.

---

## 2. Band-Pass Filtering

A fourth-order Butterworth band-pass filter preserves a selected frequency range.

```text
          Passband
      ┌───────────────┐
──────┘               └──────
      fLow           fHigh
```

This is particularly useful when the expected acoustic signal occupies a known frequency band.

---

## 3. Notch Filtering

The simulator uses an IIR notch filter to selectively suppress a narrow frequency component.

This is especially relevant for:

```text
50 Hz electrical interference
60 Hz electrical interference
```

and other narrowband interference sources.

---

## 4. Moving-Average Filtering

A moving-average filter is also available.

The window size is configurable:

```text
3 → 101 samples
```

and can be adjusted to study the trade-off between smoothing and signal preservation.

---

# 🔄 Zero-Phase Filtering

The Butterworth and notch filtering operations use:

```text
scipy.signal.filtfilt()
```

This performs forward and reverse filtering to minimize phase distortion.

Conceptually:

```text
Corrupted Signal
       │
       ▼
 Forward Filter
       │
       ▼
 Reverse Filter
       │
       ▼
Recovered Signal
```

This is important when comparing the recovered waveform directly with the original ground-truth signal.

---

# 📊 Recovery Performance Metrics

The application calculates six recovery indicators.

| Metric              | Purpose                                 |
| ------------------- | --------------------------------------- |
| **SNR Before**      | Signal quality before filtering         |
| **SNR After**       | Signal quality after filtering          |
| **SNR Improvement** | Quantifies recovery improvement         |
| **RMSE**            | Measures waveform reconstruction error  |
| **Correlation**     | Measures similarity to the clean signal |
| **Signal Quality**  | Overall recovery assessment             |

These are presented as instrument-style metric cards in the GUI.

---

# 📐 RMSE Analysis

Root Mean Square Error is calculated between the clean signal and recovered signal:

```text
RMSE =
√ mean[(xclean − xrecovered)²]
```

Lower RMSE indicates closer waveform reconstruction.

This is important because a filter can improve SNR while still introducing undesirable signal distortion.

---

# 🔗 Cross-Correlation

The simulator calculates normalized correlation between the clean and recovered waveforms.

Conceptually:

```text
Correlation → 1
```

indicates strong similarity between the recovered waveform and the original signal.

This complements SNR and RMSE by measuring **waveform preservation** rather than noise suppression alone.

---

# 🧠 Engineering Recovery Assessment

The simulator automatically classifies the filtering result.

### 🟢 Successful Remediation

Triggered when:

```text
SNR Improvement ≥ 2 dB
AND
Correlation > 0.85
```

This indicates significant noise suppression while maintaining good signal integrity.

### 🟡 Moderate Improvement

Triggered when SNR improves but does not reach the stronger recovery threshold.

### 🔴 Performance Degradation

Triggered when the filter reduces SNR or otherwise fails to adequately suppress noise.

The application also generates an **Engineering Evaluation Report** summarizing the noise environment, filtering strategy, SNR differential, RMSE, and correlation.

---

# 📈 Time-Domain Analysis

The simulator visualizes the signal-processing stages in the time domain:

```text
Clean Signal
     │
     ▼
Noisy Signal
     │
     ▼
Recovered Signal
```

This allows direct visual inspection of:

* Noise contamination
* Filtering effects
* Impulsive disturbances
* Waveform preservation
* Signal distortion

---

# 📡 FFT Spectral Analysis

The application also calculates FFT magnitude spectra for the noisy and recovered signals.

The frequency axis is calculated using:

```text
f = np.fft.rfftfreq(N, d=1/fs)
```

and the magnitude spectrum using:

```text
|FFT(x)| / N
```

This allows users to observe how filtering changes the frequency-domain representation.

---

# 🔬 Noise-Reduction Processing Pipeline

```text
┌──────────────────────────────┐
│     Clean Acoustic Signal    │
│                              │
│      A sin(2πft)             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Noise Generator        │
│                              │
│ Gaussian / White / Rumble    │
│ 50 Hz / 60 Hz / Impulse      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Target-SNR Scaling     │
│                              │
│ Controlled Noise Power       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Noisy Acoustic Signal   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Recovery Filter        │
│                              │
│ LPF / Band-Pass / Notch / MA │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Recovered Signal       │
└──────────────┬───────────────┘
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
     SNR      RMSE   Correlation
       │       │        │
       └───────┼────────┘
               ▼
┌──────────────────────────────┐
│   Engineering Assessment     │
│                              │
│ Successful / Moderate /      │
│ Degraded                     │
└──────────────────────────────┘
```

---

# 🖥️ Application Interface

The application uses a dark laboratory-instrument interface with two primary sections.

```text
┌──────────────────────────────────────────────────────────────┐
│             ACOUSTIC NOISE REDUCTION SIMULATOR              │
├──────────────────────┬───────────────────────────────────────┤
│                      │                                       │
│  ACOUSTIC SIGNAL     │       SYSTEM STATUS                   │
│  GENERATOR           │                                       │
│                      ├───────────────────────────────────────┤
│  NOISE ENVIRONMENT   │                                       │
│  SETUP               │       RECOVERY METRICS                │
│                      │                                       │
│  FILTERING &         │  SNR Before │ SNR After │ Improvement │
│  RECOVERY OPTIONS    │  RMSE       │ Correlation│ Quality     │
│                      ├───────────────────────────────────────┤
│  ENGINEERING REPORT  │                                       │
│                      │   WAVEFORMS & SPECTRAL ANALYSIS       │
│                      │                                       │
└──────────────────────┴───────────────────────────────────────┘
```

The GUI is implemented using **PyQt5**, with Matplotlib embedded for waveform and spectral visualization.

---

# 🧪 Example Experiments

## Experiment 1 — Gaussian Noise Reduction

Configure:

```text
Signal Frequency = 220 Hz
Noise Type       = Gaussian noise
Target SNR       = 6 dB
Filter           = Low-pass
```

Observe the change in:

* SNR
* RMSE
* Correlation
* Time-domain waveform
* FFT spectrum

---

## Experiment 2 — 50 Hz Electrical Interference

Configure:

```text
Noise Type = 50 Hz electrical interference
Filter     = Notch filtering
Cutoff     = 50 Hz
```

Observe the suppression of the narrowband interference component.

This demonstrates a practical application of notch filtering in acoustic/electronic measurement systems.

---

## Experiment 3 — 60 Hz Interference

Repeat the experiment using:

```text
Noise Type = 60 Hz electrical interference
Cutoff     = 60 Hz
```

Compare the recovery performance with the 50 Hz case.

---

## Experiment 4 — Low-Frequency Rumble

Use:

```text
Noise Type = Low-frequency rumble
Filter     = High-frequency-preserving strategy
```

Compare different cutoff settings and observe the effect on both noise suppression and waveform preservation.

---

## Experiment 5 — Impulse Noise

Select:

```text
Noise Type = Random impulse noise
```

Observe the characteristic spikes in the time-domain waveform and study how a moving-average filter responds to impulsive contamination.

---

## Experiment 6 — Filter Comparison

Keep the noise environment fixed and compare:

```text
Low-pass
Band-pass
Notch
Moving-average
```

Use:

```text
SNR Improvement
RMSE
Correlation
```

to quantitatively compare the recovery strategies.

---

# 🎓 Educational Applications

This project can be used to demonstrate:

* Acoustic Signal Processing
* Digital Signal Processing
* Noise Reduction
* Signal Recovery
* SNR
* RMSE
* Cross-Correlation
* FFT Analysis
* Frequency-Domain Filtering
* Butterworth Filters
* Notch Filters
* Moving-Average Filters
* Band-Pass Filtering
* Electrical Interference
* Impulse Noise
* Signal Conditioning
* Acoustic Instrumentation

---

# 🛠️ Technology Stack

| Technology     | Purpose                                    |
| -------------- | ------------------------------------------ |
| **Python**     | Core application                           |
| **NumPy**      | Signal generation, numerical analysis, FFT |
| **SciPy**      | Digital filtering and signal processing    |
| **PyQt5**      | Desktop GUI                                |
| **Matplotlib** | Waveform and spectral visualization        |

The implementation directly uses NumPy, SciPy signal-processing functions, PyQt5, and Matplotlib.

---

# 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/vishwakiran712/Acoustic-Noise-Reduction-Simulator.git
cd Acoustic-Noise-Reduction-Simulator
```

### 2. Install dependencies

```bash
pip install numpy scipy matplotlib PyQt5
```

### 3. Run the simulator

```bash
python app.py
```

---

# 📂 Project Structure

```text
Acoustic-Noise-Reduction-Simulator/
│
├── app.py
├── README.md
└── LICENSE
```

---

# 🔭 Possible Future Enhancements

Potential extensions include:

* Real microphone input
* WAV-file noise reduction
* Real-time noise suppression
* Adaptive filtering
* LMS adaptive filter
* RLS adaptive filter
* Wiener filtering
* Spectral subtraction
* Noise-profile estimation
* STFT-based noise reduction
* Spectrogram comparison
* Voice-specific noise reduction
* Multiple acoustic sources
* Real-time SNR monitoring
* Audio playback
* Before/after audio export
* Frequency-response visualization
* Automated filter parameter optimization

---

# 📜 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

---

# 👨‍💻 Author

**Vishwakiran B.V.S.**

Engineering • Sports Technology • Product Research • Scientific Computing • Signal Processing

GitHub: [@vishwakiran712](https://github.com/vishwakiran712)

---

# ⭐ Project

If you find this project useful for learning, experimentation, or acoustic/DSP research, consider giving the repository a ⭐.

**Repository:**
https://github.com/vishwakiran712/Acoustic-Noise-Reduction-Simulator
