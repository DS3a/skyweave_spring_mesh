import numpy as np
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display

side_length = 0.4
u_min, u_max = -side_length/2, side_length/2
v_min, v_max = -side_length/2, side_length/2

num_u = 50
num_v = 50

u = np.linspace(u_min, u_max, num_u)
v = np.linspace(v_min, v_max, num_v)

U, V = np.meshgrid(u, v)

frequency = np.pi/0.4


def gamma_sur(u, v, A=0.05, angle=np.pi, phase=np.pi/2, base_pos=np.array([0,0,0])):
    x = u
    y = v

    s = u*np.cos(angle) + v*np.sin(angle)

    z = A*np.cos(frequency*s + phase)

    offset = base_pos - np.array([0,0,A*np.cos(frequency*0 + phase)])

    x = x + offset[0]
    y = y + offset[1]
    z = z + offset[2]

    return x,y,z


fig = go.FigureWidget()

X,Y,Z = gamma_sur(U,V)

surf = fig.add_surface(x=X,y=Y,z=Z)

fig.update_layout(
    title="Developable surface",
    scene=dict(
        aspectmode='manual',
        aspectratio=dict(x=2,y=2,z=0.5)
    )
)

# sliders
amp_slider = widgets.FloatSlider(value=0.05,min=0,max=0.1,step=0.005,description='Amplitude')
angle_slider = widgets.FloatSlider(value=np.pi,min=0,max=2*np.pi,step=0.05,description='Angle')
phase_slider = widgets.FloatSlider(value=np.pi/2,min=0,max=2*np.pi,step=0.05,description='Phase')


def update(change=None):
    A = amp_slider.value
    angle = angle_slider.value
    phase = phase_slider.value
    
    X,Y,Z = gamma_sur(U,V,A=A,angle=angle,phase=phase)
    
    with fig.batch_update():
        fig.data[0].x = X
        fig.data[0].y = Y
        fig.data[0].z = Z


amp_slider.observe(update,'value')
angle_slider.observe(update,'value')
phase_slider.observe(update,'value')

display(widgets.VBox([amp_slider,angle_slider,phase_slider]))
fig.update_layout(
    title="Developable surface",
    scene=dict(
        aspectmode='manual',
        aspectratio=dict(x=2,y=2,z=0.5)
    ),
    width=1600,
    height=900,
)
fig