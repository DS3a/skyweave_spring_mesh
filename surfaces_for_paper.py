import argparse
import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

side_length = 0.4
u_min, u_max = -side_length / 2, side_length / 2
v_min, v_max = -side_length / 2, side_length / 2

num_u = 50
num_v = 50

u = np.linspace(u_min, u_max, num_u)
v = np.linspace(v_min, v_max, num_v)

U, V = np.meshgrid(u, v)

frequency = np.pi / 0.4
DEFAULT_PLOT_WIDTH = 1800
DEFAULT_PLOT_HEIGHT = 1200
MAX_AMPLITUDE_FOR_Z_SCALE = 0.1
Z_AXIS_MARGIN = 0.01


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


def format_status_text(amp, angle, phase):
    return (
        f"Amplitude: {amp:.4f} | Angle: {angle:.4f} rad | "
        f"Phase: {phase:.4f} rad | Frequency: {frequency:.4f} rad/m"
    )


def build_post_script(u_grid, v_grid):
    u_json = json.dumps(u_grid.tolist())
    v_json = json.dumps(v_grid.tolist())

    return f"""
const plotDiv = document.getElementById('{{plot_id}}');
const frequency = {frequency};
const uGrid = {u_json};
const vGrid = {v_json};

const controls = document.createElement('div');
controls.style.maxWidth = '1000px';
controls.style.width = '100%';
controls.style.margin = '8px auto 0 auto';
controls.style.fontFamily = 'sans-serif';
controls.style.padding = '6px 12px';
controls.style.border = '1px solid #ddd';
controls.style.borderRadius = '8px';

const title = document.createElement('div');
title.textContent = 'Surface controls';
title.style.fontWeight = '600';
title.style.marginBottom = '8px';
controls.appendChild(title);

function addSliderRow(label, min, max, step, value) {{
    const row = document.createElement('div');
    row.style.display = 'grid';
    row.style.gridTemplateColumns = '120px 1fr 120px';
    row.style.alignItems = 'center';
    row.style.gap = '8px';
    row.style.marginBottom = '8px';

    const name = document.createElement('label');
    name.textContent = label;

    const input = document.createElement('input');
    input.type = 'range';
    input.min = min;
    input.max = max;
    input.step = step;
    input.value = value;
    input.style.width = '100%';

    const valueText = document.createElement('div');
    valueText.style.textAlign = 'right';

    row.appendChild(name);
    row.appendChild(input);
    row.appendChild(valueText);
    controls.appendChild(row);
    return {{ input, valueText }};
}}

const amp = addSliderRow('Amplitude', 0.0, 0.1, 0.005, plotDiv.data[0].meta.amp);
const angle = addSliderRow('Angle (rad)', 0.0, 2 * Math.PI, 0.05, plotDiv.data[0].meta.angle);
const phase = addSliderRow('Phase (rad)', -Math.PI, Math.PI, 0.05, plotDiv.data[0].meta.phase);

const freqLine = document.createElement('div');
freqLine.textContent = `Frequency (constant): ${{frequency.toFixed(4)}} rad/m`;
freqLine.style.marginTop = '4px';
freqLine.style.fontSize = '14px';
controls.appendChild(freqLine);

plotDiv.parentNode.insertBefore(controls, plotDiv);

function computeSurface(ampVal, angleVal, phaseVal) {{
    const z = [];
    const phaseCos = Math.cos(phaseVal);

    for (let i = 0; i < uGrid.length; i += 1) {{
        const row = [];
        for (let j = 0; j < uGrid[i].length; j += 1) {{
            const s = uGrid[i][j] * Math.cos(angleVal) + vGrid[i][j] * Math.sin(angleVal);
            row.push(ampVal * Math.cos(frequency * s + phaseVal) - ampVal * phaseCos);
        }}
        z.push(row);
    }}

    return z;
}}

function updatePlot() {{
    const ampVal = Number(amp.input.value);
    const angleVal = Number(angle.input.value);
    const phaseVal = Number(phase.input.value);

    amp.valueText.textContent = ampVal.toFixed(4);
    angle.valueText.textContent = angleVal.toFixed(4);
    phase.valueText.textContent = phaseVal.toFixed(4);

    const z = computeSurface(ampVal, angleVal, phaseVal);
    const statusText = `Amplitude: ${{ampVal.toFixed(4)}} | Angle: ${{angleVal.toFixed(4)}} rad | Phase: ${{phaseVal.toFixed(4)}} rad | Frequency: ${{frequency.toFixed(4)}} rad/m`;

    Plotly.restyle(plotDiv, {{ z: [z], meta: [{{ amp: ampVal, angle: angleVal, phase: phaseVal }}] }}, [0]);
    Plotly.relayout(plotDiv, {{ 'annotations[0].text': statusText }});
}}

function buildControlsInWindow(win) {{
    const doc = win.document;
    doc.open();
    doc.write(`<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Surface controls</title>
  <style>
    body {{ font-family: sans-serif; margin: 0; padding: 12px; }}
    .row {{ display: grid; grid-template-columns: 130px 1fr 110px; gap: 8px; align-items: center; margin-bottom: 10px; }}
    .panel {{ border: 1px solid #ddd; border-radius: 8px; padding: 10px; }}
    .title {{ font-weight: 600; margin-bottom: 10px; }}
    .meta {{ margin-top: 8px; font-size: 14px; }}
  </style>
</head>
<body>
  <div class=\"panel\">
    <div class=\"title\">Surface controls</div>
    <div class=\"row\"><label for=\"amp\">Amplitude</label><input id=\"amp\" type=\"range\" min=\"-0.05\" max=\"0.05\" step=\"0.005\"><div id=\"ampVal\"></div></div>
    <div class=\"row\"><label for=\"angle\">Angle (rad)</label><input id=\"angle\" type=\"range\" min=\"0\" max=\"${{2 * Math.PI}}\" step=\"0.05\"><div id=\"angleVal\"></div></div>
    <div class=\"row\"><label for=\"phase\">Phase (rad)</label><input id=\"phase\" type=\"range\" min=\"${{-Math.PI}}\" max=\"${{Math.PI}}\" step=\"0.05\"><div id=\"phaseVal\"></div></div>
    <div class=\"meta\" id=\"freq\"></div>
  </div>
</body>
</html>`);
    doc.close();

    const ampInput = doc.getElementById('amp');
    const angleInput = doc.getElementById('angle');
    const phaseInput = doc.getElementById('phase');
    const ampVal = doc.getElementById('ampVal');
    const angleVal = doc.getElementById('angleVal');
    const phaseVal = doc.getElementById('phaseVal');
    const freq = doc.getElementById('freq');

    ampInput.value = String(plotDiv.data[0].meta.amp);
    angleInput.value = String(plotDiv.data[0].meta.angle);
    phaseInput.value = String(plotDiv.data[0].meta.phase);
    freq.textContent = `Frequency (constant): ${{frequency.toFixed(4)}} rad/m`;

    const sync = () => {{
        const amp = Number(ampInput.value);
        const angle = Number(angleInput.value);
        const phase = Number(phaseInput.value);
        ampVal.textContent = amp.toFixed(4);
        angleVal.textContent = angle.toFixed(4);
        phaseVal.textContent = phase.toFixed(4);
        updatePlot(amp, angle, phase);
    }};

    ampInput.addEventListener('input', sync);
    angleInput.addEventListener('input', sync);
    phaseInput.addEventListener('input', sync);
    sync();
}}

const openControlsBtn = document.createElement('button');
openControlsBtn.textContent = 'Open controls window';
openControlsBtn.style.position = 'fixed';
openControlsBtn.style.top = '10px';
openControlsBtn.style.right = '10px';
openControlsBtn.style.zIndex = '10';
openControlsBtn.style.padding = '8px 10px';
openControlsBtn.style.border = '1px solid #ccc';
openControlsBtn.style.background = '#fff';
openControlsBtn.style.borderRadius = '6px';
openControlsBtn.style.cursor = 'pointer';
document.body.appendChild(openControlsBtn);

let controlsWindow = null;
function openControlsWindow() {{
    if (controlsWindow && !controlsWindow.closed) {{
        controlsWindow.focus();
        return;
    }}
    controlsWindow = window.open('', 'surface_controls', 'width=560,height=320,left=40,top=40');
    if (!controlsWindow) {{
        alert('Popup blocked. Please allow popups and click "Open controls window" again.');
        return;
    }}
    buildControlsInWindow(controlsWindow);
}}

openControlsBtn.addEventListener('click', openControlsWindow);
setTimeout(openControlsWindow, 150);
amp.input.addEventListener('input', updatePlot);
angle.input.addEventListener('input', updatePlot);
phase.input.addEventListener('input', updatePlot);

updatePlot();
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Render interactive developable surface in Plotly.")
    parser.add_argument("--amplitude", type=float, default=0.05, help="Initial amplitude value.")
    parser.add_argument("--angle", type=float, default=float(np.pi), help="Initial angle in radians.")
    parser.add_argument("--phase", type=float, default=float(np.pi / 2), help="Initial phase in radians.")
    parser.add_argument("--width", type=int, default=DEFAULT_PLOT_WIDTH, help="Plot width in pixels.")
    parser.add_argument("--height", type=int, default=DEFAULT_PLOT_HEIGHT, help="Plot height in pixels.")
    parser.add_argument(
        "--output",
        type=str,
        default="surface_controls_plotly.html",
        help="Output HTML file path.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    x_vals, y_vals, z_vals = gamma_sur(U, V, A=args.amplitude, angle=args.angle, phase=args.phase)
    status_text = format_status_text(args.amplitude, args.angle, args.phase)

    fig = go.Figure(
        data=[
            go.Surface(
                x=x_vals,
                y=y_vals,
                z=z_vals,
                colorscale="Viridis",
                showscale=False,
                meta={"amp": args.amplitude, "angle": args.angle, "phase": args.phase},
            )
        ]
    )

    fig.update_layout(
        title="Developable surface",
        width=args.width,
        height=args.height,
        margin=dict(l=20, r=20, b=20, t=70),
        scene=dict(
            xaxis_title="x",
            yaxis_title="y",
            zaxis_title="z",
            zaxis=dict(
                range=[
                    -(MAX_AMPLITUDE_FOR_Z_SCALE + Z_AXIS_MARGIN),
                    MAX_AMPLITUDE_FOR_Z_SCALE + Z_AXIS_MARGIN,
                ],
                autorange=False,
            ),
            aspectmode="manual",
            aspectratio=dict(x=2, y=2, z=0.5),
            domain=dict(x=[0.0, 1.0], y=[0.0, 1.0]),
        ),
        annotations=[
            dict(
                text=status_text,
                x=0.5,
                y=1.04,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14),
            )
        ],
    )

    plot_div = pio.to_html(
        fig,
        include_plotlyjs="cdn",
        full_html=False,
        post_script=build_post_script(U, V),
        default_width=f"{args.width}px",
        default_height=f"{args.height}px",
    )

    centered_html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Developable surface</title>
  <style>
    body {{
      margin: 0;
      padding: 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      background: #ffffff;
    }}
    .plot-wrap {{
      width: 100%;
      display: flex;
      justify-content: center;
    }}
  </style>
</head>
<body>
  <div class=\"plot-wrap\">{plot_div}</div>
</body>
</html>
"""

    output_path = Path(args.output)
    output_path.write_text(full_screen_html, encoding="utf-8")

    print(f"Wrote interactive plot to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
