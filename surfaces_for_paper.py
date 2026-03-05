import argparse
import tkinter as tk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

side_length = 0.4
u_min, u_max = -side_length / 2, side_length / 2
v_min, v_max = -side_length / 2, side_length / 2

num_u = 50
num_v = 50

u = np.linspace(u_min, u_max, num_u)
v = np.linspace(v_min, v_max, num_v)

U, V = np.meshgrid(u, v)

frequency = np.pi / 0.4


def gamma_sur(u_vals, v_vals, A=0.05, angle=np.pi, phase=np.pi / 2, base_pos=np.array([0, 0, 0])):
    x_vals = u_vals
    y_vals = v_vals

    s_vals = u_vals * np.cos(angle) + v_vals * np.sin(angle)

    z_vals = A * np.cos(frequency * s_vals + phase)

    offset = base_pos - np.array([0, 0, A * np.cos(phase)])

    x_vals = x_vals + offset[0]
    y_vals = y_vals + offset[1]
    z_vals = z_vals + offset[2]

    return x_vals, y_vals, z_vals


class SurfaceController:
    def __init__(self, start_amp=0.05, start_angle=np.pi, start_phase=np.pi / 2):
        self.amp = start_amp
        self.angle = start_angle
        self.phase = start_phase

        self.fig = None
        self.ax = None
        self.surface = None
        self.slider_fig = None

        # Keep references so widgets/callbacks stay alive.
        self.amp_slider = None
        self.angle_slider = None
        self.phase_slider = None
        self._plot_scroll_cid = None

    def _draw_surface(self):
        x_vals, y_vals, z_vals = gamma_sur(U, V, A=self.amp, angle=self.angle, phase=self.phase)
        if self.surface is not None:
            self.surface.remove()
        self.surface = self.ax.plot_surface(x_vals, y_vals, z_vals, cmap="viridis", edgecolor="none")
        self.fig.canvas.draw_idle()

    def _update_amp(self, val):
        self.amp = val
        self._draw_surface()

    def _update_angle(self, val):
        self.angle = val
        self._draw_surface()

    def _update_phase(self, val):
        self.phase = val
        self._draw_surface()

    def _on_scroll_zoom(self, event):
        if event.inaxes != self.ax:
            return

        scale = 0.90 if event.button == "up" else 1.10
        for get_lim, set_lim in (
            (self.ax.get_xlim3d, self.ax.set_xlim3d),
            (self.ax.get_ylim3d, self.ax.set_ylim3d),
            (self.ax.get_zlim3d, self.ax.set_zlim3d),
        ):
            lo, hi = get_lim()
            center = (lo + hi) / 2.0
            half = (hi - lo) * scale / 2.0
            set_lim(center - half, center + half)

        self.fig.canvas.draw_idle()

    def setup_plot_window(self):
        scale = 2
        self.fig = plt.figure("Developable surface", figsize=(20, 16))
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.set_title("Developable surface")
        self.ax.set_box_aspect((2*scale, 2*scale, 0.5*scale))
        
        self.ax.set_ylabel("y")
        self.ax.set_zlabel("z")

        self._draw_surface()

        # Explicitly enable built-in navigation and add wheel zoom.
        self.ax.set_navigate(True)
        self._plot_scroll_cid = self.fig.canvas.mpl_connect("scroll_event", self._on_scroll_zoom)

    def setup_slider_window(self):
        self.slider_fig = plt.figure("Surface sliders", figsize=(7, 3.5))

        amp_ax = self.slider_fig.add_axes([0.15, 0.70, 0.75, 0.08])
        angle_ax = self.slider_fig.add_axes([0.15, 0.45, 0.75, 0.08])
        phase_ax = self.slider_fig.add_axes([0.15, 0.20, 0.75, 0.08])

        self.amp_slider = Slider(amp_ax, "Amplitude", 0.0, 0.1, valinit=self.amp, valstep=0.005)
        self.angle_slider = Slider(angle_ax, "Angle", 0.0, 2 * np.pi, valinit=self.angle, valstep=0.05)
        self.phase_slider = Slider(phase_ax, "Phase", -np.pi, np.pi, valinit=self.phase, valstep=0.05)

        self.amp_slider.on_changed(self._update_amp)
        self.angle_slider.on_changed(self._update_angle)
        self.phase_slider.on_changed(self._update_phase)

    def arrange_windows(self):
        root = tk.Tk()
        root.withdraw()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.destroy()

        # Best-effort geometry placement for TkAgg; ignored by other backends.
        plot_mgr = self.fig.canvas.manager if self.fig is not None else None
        slider_mgr = self.slider_fig.canvas.manager if self.slider_fig is not None else None

        try:
            if plot_mgr and hasattr(plot_mgr, "window") and hasattr(plot_mgr.window, "wm_geometry"):
                plot_mgr.window.wm_geometry("1920x1080+80+80")
        except Exception:
            pass

        try:
            if slider_mgr and hasattr(slider_mgr, "window") and hasattr(slider_mgr.window, "wm_geometry"):
                x_pos = min(screen_w - 760, 1250)
                y_pos = min(screen_h - 420, 50)
                slider_mgr.window.wm_geometry(f"740x360+{x_pos}+{y_pos}")
        except Exception:
            pass


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Render a developable surface with external slider controls. "
            "Use mouse drag to rotate and mouse wheel to zoom in the surface window."
        )
    )
    parser.add_argument("--amplitude", type=float, default=0.05, help="Initial amplitude value.")
    parser.add_argument("--angle", type=float, default=float(np.pi), help="Initial angle in radians.")
    parser.add_argument("--phase", type=float, default=float(np.pi / 2), help="Initial phase in radians.")
    return parser.parse_args()


def main():
    args = parse_args()

    controller = SurfaceController(start_amp=args.amplitude, start_angle=args.angle, start_phase=args.phase)
    controller.setup_plot_window()
    controller.setup_slider_window()
    controller.arrange_windows()

    plt.show()


if __name__ == "__main__":
    main()
