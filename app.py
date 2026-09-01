import sys
import numpy as np
from scipy import signal as sp_signal

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QComboBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QGroupBox, QFrame, QSplitter, QScrollArea,
    QTextBrowser
)
from PyQt5.QtCore import Qt

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# -------------------------------------------------------------------------
# Custom Laboratory Dark Styling (CSS)
# -------------------------------------------------------------------------
DARK_STYLE = """
QMainWindow {
    background-color: #0D1117;
}
QWidget {
    color: #C9D1D9;
    font-family: "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 11px;
}
QGroupBox {
    border: 1px solid #21262D;
    border-radius: 6px;
    margin-top: 10px;
    font-weight: bold;
    color: #58A6FF;
    background-color: #161B22;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    background-color: #161B22;
    border-radius: 3px;
}
QLabel {
    color: #8B949E;
}
QDoubleSpinBox, QSpinBox, QComboBox {
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 4px;
    padding: 4px 6px;
    color: #58A6FF;
    font-weight: bold;
}
QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #58A6FF;
}
QPushButton {
    background-color: #21262D;
    border: 1px solid #30363D;
    border-radius: 4px;
    color: #C9D1D9;
    font-weight: bold;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #30363D;
    border-color: #58A6FF;
    color: #58A6FF;
}
QFrame#metricCard {
    background-color: #0D1117;
    border: 1px solid #21262D;
    border-radius: 6px;
}
QTextBrowser {
    background-color: #0D1117;
    border: 1px solid #21262D;
    border-radius: 4px;
    color: #C9D1D9;
    padding: 6px;
}
"""

# -------------------------------------------------------------------------
# Main Application GUI Class
# -------------------------------------------------------------------------
class AcousticNoiseReductionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Acoustic Noise Reduction Simulator")
        self.resize(1380, 880)
        self.setMinimumSize(1024, 720)

        # DSP Setup
        self.fs = 8000  # Sampling frequency (Hz)
        self.duration = 0.5  # Signal length (seconds)
        self.t = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)

        # Signal State
        self.clean_sig = None
        self.noisy_sig = None
        self.recovered_sig = None

        self.init_ui()
        self.process_pipeline()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # =================================---------------------------------
        # LEFT PANEL: Parameters & Controls
        # =================================---------------------------------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        ctrl_layout = QVBoxLayout(scroll_content)

        # 1. Acoustic Signal Configuration
        group_sig = QGroupBox("1. ACOUSTIC SIGNAL GENERATOR")
        grid_sig = QGridLayout(group_sig)
        grid_sig.setSpacing(6)

        grid_sig.addWidget(QLabel("Signal Freq (Hz):"), 0, 0)
        self.spin_sig_freq = QDoubleSpinBox()
        self.spin_sig_freq.setRange(20.0, 2000.0)
        self.spin_sig_freq.setValue(220.0)
        self.spin_sig_freq.setSingleStep(10.0)
        grid_sig.addWidget(self.spin_sig_freq, 0, 1)

        grid_sig.addWidget(QLabel("Signal Amp:"), 1, 0)
        self.spin_sig_amp = QDoubleSpinBox()
        self.spin_sig_amp.setRange(0.1, 5.0)
        self.spin_sig_amp.setValue(1.0)
        grid_sig.addWidget(self.spin_sig_amp, 1, 1)

        ctrl_layout.addWidget(group_sig)

        # 2. Noise Corruption Setup
        group_noise = QGroupBox("2. NOISE ENVIRONMENT SETUP")
        grid_noise = QGridLayout(group_noise)
        grid_noise.setSpacing(6)

        grid_noise.addWidget(QLabel("Noise Type:"), 0, 0)
        self.combo_noise_type = QComboBox()
        self.combo_noise_type.addItems([
            "Gaussian noise",
            "White noise",
            "Low-frequency rumble",
            "50 Hz electrical interference",
            "60 Hz electrical interference",
            "Random impulse noise"
        ])
        grid_noise.addWidget(self.combo_noise_type, 0, 1)

        grid_noise.addWidget(QLabel("Noise Amp:"), 1, 0)
        self.spin_noise_amp = QDoubleSpinBox()
        self.spin_noise_amp.setRange(0.01, 3.0)
        self.spin_noise_amp.setValue(0.35)
        self.spin_noise_amp.setSingleStep(0.05)
        grid_noise.addWidget(self.spin_noise_amp, 1, 1)

        grid_noise.addWidget(QLabel("Target SNR (dB):"), 2, 0)
        self.spin_target_snr = QDoubleSpinBox()
        self.spin_target_snr.setRange(-10.0, 30.0)
        self.spin_target_snr.setValue(6.0)
        grid_noise.addWidget(self.spin_target_snr, 2, 1)

        ctrl_layout.addWidget(group_noise)

        # 3. DSP Filter Configuration
        group_filter = QGroupBox("3. FILTERING & RECOVERY OPTIONS")
        grid_filter = QGridLayout(group_filter)
        grid_filter.setSpacing(6)

        grid_filter.addWidget(QLabel("Filter Type:"), 0, 0)
        self.combo_filter_type = QComboBox()
        self.combo_filter_type.addItems([
            "Low-pass filtering",
            "Band-pass filtering",
            "Notch filtering",
            "Moving-average filtering"
        ])
        grid_filter.addWidget(self.combo_filter_type, 0, 1)

        grid_filter.addWidget(QLabel("Filter Cutoff / Fc (Hz):"), 1, 0)
        self.spin_cutoff1 = QDoubleSpinBox()
        self.spin_cutoff1.setRange(10.0, 3800.0)
        self.spin_cutoff1.setValue(400.0)
        self.spin_cutoff1.setSingleStep(20.0)
        grid_filter.addWidget(self.spin_cutoff1, 1, 1)

        self.lbl_cutoff2 = QLabel("Cutoff High (Hz):")
        grid_filter.addWidget(self.lbl_cutoff2, 2, 0)
        self.spin_cutoff2 = QDoubleSpinBox()
        self.spin_cutoff2.setRange(20.0, 3900.0)
        self.spin_cutoff2.setValue(800.0)
        self.spin_cutoff2.setSingleStep(20.0)
        grid_filter.addWidget(self.spin_cutoff2, 2, 1)

        grid_filter.addWidget(QLabel("Moving Avg Window:"), 3, 0)
        self.spin_ma_window = QSpinBox()
        self.spin_ma_window.setRange(3, 101)
        self.spin_ma_window.setValue(11)
        self.spin_ma_window.setSingleStep(2)
        grid_filter.addWidget(self.spin_ma_window, 3, 1)

        ctrl_layout.addWidget(group_filter)

        # 4. Engineering Summary Report
        group_report = QGroupBox("ENGINEERING EVALUATION REPORT")
        layout_report = QVBoxLayout(group_report)
        self.report_browser = QTextBrowser()
        self.report_browser.setFixedHeight(180)
        layout_report.addWidget(self.report_browser)

        ctrl_layout.addWidget(group_report)
        ctrl_layout.addStretch()

        scroll.setWidget(scroll_content)
        left_layout.addWidget(scroll)

        # Event Signals
        for spin in [self.spin_sig_freq, self.spin_sig_amp, self.spin_noise_amp,
                     self.spin_target_snr, self.spin_cutoff1, self.spin_cutoff2,
                     self.spin_ma_window]:
            spin.valueChanged.connect(self.process_pipeline)

        self.combo_noise_type.currentIndexChanged.connect(self.process_pipeline)
        self.combo_filter_type.currentIndexChanged.connect(self.on_filter_type_changed)

        # =================================---------------------------------
        # RIGHT PANEL: Status, Performance Metrics & Visual Displays
        # =================================---------------------------------
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Status Banner
        self.lbl_status = QLabel("SYSTEM STATUS: Acoustic Engine Active")
        self.lbl_status.setStyleSheet(
            "background-color: #0D1117; color: #3FB950; font-weight: bold; "
            "padding: 6px; border-radius: 4px; border: 1px solid #21262D;"
        )
        right_layout.addWidget(self.lbl_status)

        # Metrics Analytics Grid
        metrics_group = QGroupBox("CALCULATED RECOVERY METRICS")
        grid_metrics = QGridLayout(metrics_group)
        grid_metrics.setSpacing(6)

        self.lbl_snr_before = self.create_metric_card("SNR Before", "0.0 dB", grid_metrics, 0, 0)
        self.lbl_snr_after = self.create_metric_card("SNR After", "0.0 dB", grid_metrics, 0, 1)
        self.lbl_snr_imp = self.create_metric_card("SNR Improvement", "+0.0 dB", grid_metrics, 0, 2)

        self.lbl_rmse = self.create_metric_card("RMSE", "0.0000", grid_metrics, 1, 0)
        self.lbl_corr = self.create_metric_card("Correlation", "0.0000", grid_metrics, 1, 1)
        self.lbl_recovery_status = self.create_metric_card("Signal Quality", "Evaluating", grid_metrics, 1, 2)

        right_layout.addWidget(metrics_group)

        # Matplotlib Visualization Canvas
        plots_group = QGroupBox("WAVEFORMS & SPECTRAL ANALYSIS")
        layout_plots = QVBoxLayout(plots_group)

        self.fig = Figure(figsize=(9, 7), facecolor='#161B22')
        self.canvas = FigureCanvas(self.fig)
        layout_plots.addWidget(self.canvas)

        right_layout.addWidget(plots_group, stretch=1)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([380, 960])

        self.on_filter_type_changed()

    def create_metric_card(self, title, default_val, layout, row, col):
        card = QFrame()
        card.setObjectName("metricCard")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(6, 4, 6, 4)

        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet("color: #8B949E; font-size: 10px; font-weight: bold;")
        lbl_val = QLabel(default_val)
        lbl_val.setStyleSheet("color: #58A6FF; font-size: 13px; font-weight: bold;")

        vbox.addWidget(lbl_title)
        vbox.addWidget(lbl_val)
        layout.addWidget(card, row, col)
        return lbl_val

    def on_filter_type_changed(self):
        f_type = self.combo_filter_type.currentText()
        is_bp = f_type == "Band-pass filtering"
        self.lbl_cutoff2.setVisible(is_bp)
        self.spin_cutoff2.setVisible(is_bp)
        self.process_pipeline()

    def generate_noise(self, noise_type, N):
        np.random.seed(42)  # Fixed seed for static reproducibility
        amp = self.spin_noise_amp.value()

        if noise_type == "Gaussian noise":
            return np.random.normal(0, amp, N)
        elif noise_type == "White noise":
            return np.random.uniform(-amp, amp, N)
        elif noise_type == "Low-frequency rumble":
            rumble_raw = np.random.normal(0, amp, N)
            b, a = sp_signal.butter(3, 40.0 / (self.fs / 2.0), btype='low')
            return sp_signal.filtfilt(b, a, rumble_raw) * 2.5
        elif noise_type == "50 Hz electrical interference":
            harmonics = np.sin(2 * np.pi * 50 * self.t) + 0.3 * np.sin(2 * np.pi * 150 * self.t)
            return amp * harmonics
        elif noise_type == "60 Hz electrical interference":
            harmonics = np.sin(2 * np.pi * 60 * self.t) + 0.3 * np.sin(2 * np.pi * 180 * self.t)
            return amp * harmonics
        elif noise_type == "Random impulse noise":
            impulses = np.zeros(N)
            num_spikes = int(0.015 * N)
            indices = np.random.choice(N, num_spikes, replace=False)
            impulses[indices] = np.random.choice([-1, 1], num_spikes) * amp * 4.0
            return impulses
        return np.zeros(N)

    def apply_dsp_filter(self, noisy_sig, filter_type):
        nyq = self.fs / 2.0
        fc1 = self.spin_cutoff1.value()
        fc2 = self.spin_cutoff2.value()

        if filter_type == "Low-pass filtering":
            fc = min(max(fc1, 1.0), nyq - 10.0)
            b, a = sp_signal.butter(4, fc / nyq, btype='low')
            return sp_signal.filtfilt(b, a, noisy_sig)

        elif filter_type == "Band-pass filtering":
            f_low = min(max(fc1, 1.0), nyq - 20.0)
            f_high = min(max(fc2, f_low + 10.0), nyq - 10.0)
            b, a = sp_signal.butter(4, [f_low / nyq, f_high / nyq], btype='bandpass')
            return sp_signal.filtfilt(b, a, noisy_sig)

        elif filter_type == "Notch filtering":
            f_notch = min(max(fc1, 10.0), nyq - 10.0)
            w0 = f_notch / nyq
            bw = 10.0 / nyq  # Bandwidth
            b, a = sp_signal.iirnotch(w0, Q=f_notch / 10.0)
            return sp_signal.filtfilt(b, a, noisy_sig)

        elif filter_type == "Moving-average filtering":
            w_size = self.spin_ma_window.value()
            window = np.ones(w_size) / w_size
            return np.convolve(noisy_sig, window, mode='same')

        return noisy_sig.copy()

    def process_pipeline(self):
        N = len(self.t)

        # 1. Generate Pure Acoustic Signal
        f_sig = self.spin_sig_freq.value()
        a_sig = self.spin_sig_amp.value()
        self.clean_sig = a_sig * np.sin(2 * np.pi * f_sig * self.t)

        # 2. Synthesize & Scale Noise
        noise_type = self.combo_noise_type.currentText()
        raw_noise = self.generate_noise(noise_type, N)

        # Calibrate noise level to achieve target SNR
        p_clean = np.mean(self.clean_sig**2)
        target_snr_db = self.spin_target_snr.value()
        target_p_noise = p_clean / (10.0 ** (target_snr_db / 10.0))

        current_p_noise = np.mean(raw_noise**2)
        if current_p_noise > 0:
            scaled_noise = raw_noise * np.sqrt(target_p_noise / current_p_noise)
        else:
            scaled_noise = raw_noise

        self.noisy_sig = self.clean_sig + scaled_noise

        # 3. Apply Selected Recovery Filter
        filter_type = self.combo_filter_type.currentText()
        self.recovered_sig = self.apply_dsp_filter(self.noisy_sig, filter_type)

        # 4. Statistical Metrics Evaluation
        noise_pre = self.noisy_sig - self.clean_sig
        noise_post = self.recovered_sig - self.clean_sig

        p_noise_pre = np.mean(noise_pre**2)
        p_noise_post = np.mean(noise_post**2)

        snr_before = 10 * np.log10(p_clean / max(1e-12, p_noise_pre))
        snr_after = 10 * np.log10(p_clean / max(1e-12, p_noise_post))
        snr_imp = snr_after - snr_before

        rmse = np.sqrt(np.mean((self.clean_sig - self.recovered_sig)**2))

        norm_clean = self.clean_sig - np.mean(self.clean_sig)
        norm_rec = self.recovered_sig - np.mean(self.recovered_sig)
        denom = np.sqrt(np.sum(norm_clean**2) * np.sum(norm_rec**2))
        corr = np.sum(norm_clean * norm_rec) / denom if denom > 0 else 0.0

        # Update Metrics UI
        self.lbl_snr_before.setText(f"{snr_before:.2f} dB")
        self.lbl_snr_after.setText(f"{snr_after:.2f} dB")
        self.lbl_snr_imp.setText(f"{snr_imp:+.2f} dB")
        self.lbl_rmse.setText(f"{rmse:.4f}")
        self.lbl_corr.setText(f"{corr:.4f}")

        status_str = "Improved" if snr_imp > 0.5 else ("Degraded" if snr_imp < -0.5 else "Neutral")
        color_str = "#3FB950" if snr_imp > 0.5 else ("#F85149" if snr_imp < -0.5 else "#D29922")
        self.lbl_recovery_status.setText(status_str)
        self.lbl_recovery_status.setStyleSheet(f"color: {color_str}; font-size: 13px; font-weight: bold;")

        # 5. Generate Engineering Evaluation Report
        self.generate_engineering_report(
            noise_type, filter_type, snr_before, snr_after, snr_imp, rmse, corr
        )

        # 6. Render Plots
        self.plot_all()

    def generate_engineering_report(self, noise_type, filter_type, snr_before, snr_after, snr_imp, rmse, corr):
        if snr_imp >= 2.0 and corr > 0.85:
            assessment = "<b style='color: #3FB950;'>SUCCESSFUL REMEDIATION:</b> The applied filtering strategy significantly attenuated corrupting noise while preserving target acoustic signal integrity."
        elif snr_imp > 0.0:
            assessment = "<b style='color: #D29922;'>MODERATE IMPROVEMENT:</b> Minor noise suppression was achieved. Fine-tuning cutoff parameters or selecting an alternative filter structure is recommended."
        else:
            assessment = "<b style='color: #F85149;'>PERFORMANCE DEGRADATION:</b> The filter attenuated critical fundamental signal frequencies or failed to suppress noise. Alternative filtering is required."

        html = f"""
        <style>
            body {{ font-family: sans-serif; font-size: 11px; color: #C9D1D9; line-height: 1.35; }}
            h3 {{ color: #58A6FF; margin-top: 0px; margin-bottom: 4px; font-size: 12px; }}
            ul {{ margin-top: 2px; padding-left: 16px; }}
            li {{ margin-bottom: 2px; }}
        </style>
        <h3>Engineering Evaluation Report</h3>
        {assessment}
        <br><br>
        <b>Technical Configuration & Assessment Summary:</b>
        <ul>
            <li><b>Noise Environment:</b> {noise_type}</li>
            <li><b>Filtering Strategy:</b> {filter_type}</li>
            <li><b>SNR Differential:</b> {snr_before:.2f} dB &rarr; {snr_after:.2f} dB (<b>{snr_imp:+.2f} dB</b>)</li>
            <li><b>Waveform Distortion (RMSE):</b> {rmse:.4f}</li>
            <li><b>Cross-Correlation:</b> {corr:.4f}</li>
        </ul>
        """
        self.report_browser.setHtml(html)

    def plot_all(self):
        self.fig.clear()

        grid_c = '#21262D'
        text_c = '#8B949E'

        # FFT Analysis Computations
        N = len(self.clean_sig)
        fft_noisy = np.abs(np.fft.rfft(self.noisy_sig)) / N
        fft_rec = np.abs(np.fft.rfft(self.recovered_sig)) / N
        fft_freqs = np.fft.rfftfreq(N, d=1/self.fs)

        # 1. Subplot 1: Time-Domain Waveform Overlay
        ax1 = self.fig.add_subplot(211)
        ax1.set_facecolor('#0D1117')

        # Display first 25 ms for clear waveform visualization
        disp_pts = int(0.025 * self.fs)
        t_ms = self.t[:disp_pts] * 1000.0

        ax1.plot(t_ms, self.noisy_sig[:disp_pts], color='#F85149', alpha=0.4, label="Noisy Signal")
        ax1.plot(t_ms, self.clean_sig[:disp_pts], color='#8B949E', linestyle='--', linewidth=1.2, label="Clean Reference")
        ax1.plot(t_ms, self.recovered_sig[:disp_pts], color='#58A6FF', linewidth=1.5, label="Recovered Signal")

        ax1.set_title("Time-Domain Acoustic Waveforms", color='#58A6FF', fontsize=9, fontweight='bold', loc='left')
        ax1.set_xlabel("Time (ms)", color=text_c, fontsize=8)
        ax1.set_ylabel("Amplitude (V)", color=text_c, fontsize=8)
        ax1.tick_params(colors=text_c, labelsize=7)
        ax1.grid(True, linestyle='--', alpha=0.3, color=grid_c)
        ax1.legend(facecolor='#161B22', edgecolor=grid_c, labelcolor=text_c, fontsize=7, loc='upper right')

        # 2. Subplot 2: FFT Spectral Analysis (Before vs After)
        ax2 = self.fig.add_subplot(212)
        ax2.set_facecolor('#0D1117')

        ax2.plot(fft_freqs, 20 * np.log10(np.maximum(1e-4, fft_noisy)), color='#F85149', alpha=0.5, label="FFT Before Processing")
        ax2.plot(fft_freqs, 20 * np.log10(np.maximum(1e-4, fft_rec)), color='#3FB950', linewidth=1.3, label="FFT After Processing")

        ax2.set_title("FFT Spectral Analysis (Before vs After Processing)", color='#3FB950', fontsize=9, fontweight='bold', loc='left')
        ax2.set_xlabel("Frequency (Hz)", color=text_c, fontsize=8)
        ax2.set_ylabel("Magnitude (dB)", color=text_c, fontsize=8)
        ax2.tick_params(colors=text_c, labelsize=7)
        ax2.grid(True, linestyle='--', alpha=0.3, color=grid_c)
        ax2.legend(facecolor='#161B22', edgecolor=grid_c, labelcolor=text_c, fontsize=7, loc='upper right')

        for ax in [ax1, ax2]:
            for spine in ax.spines.values():
                spine.set_color(grid_c)

        self.fig.tight_layout()
        self.canvas.draw()


# -------------------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(DARK_STYLE)

    window = AcousticNoiseReductionApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()