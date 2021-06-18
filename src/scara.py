#!/usr/bin/env python3

import numpy as np
from math import pi
import plotly.offline as py
import plotly.graph_objs as go
from geometry_msgs.msg import Point
from tf.transformations import euler_from_quaternion, quaternion_from_euler
import rospy
from homework.srv import CheckTarget, CheckTargetRequest, CheckTargetResponse

# Link lengths
d1 = 0.4
a1 = 0.3
a2 = 0.3
d4 = -0.5

# Angles
theta1 = 0
theta2 = 0
theta3 = 0
theta4 = 0

# DH parameter table
DH_table = [
    [0, a1, d1, theta1],
    [0, a2, 0, theta2],
    [0, 0, theta3, 0],
    [pi, 0, d4, theta4]
]

# Homogeneous Transformation Matrices
H0_e = [
    [np.cos(theta1+theta2+theta4), np.sin(theta1+theta2+theta4), 0, a1*np.cos(theta1)+a2*np.cos(theta1+theta2)],
    [np.sin(theta1+theta2+theta4), -np.cos(theta1+theta2+theta4), 0, a1*np.sin(theta1)+a2*np.sin(theta1+theta2)],
    [0, 0, -1, d1 + theta3 + d4],
    [0, 0, 0, 1]
]


def fk(configuration):
    theta1, theta2, theta3, theta4 = configuration
    return (
        a1*np.cos(theta1)+a2*np.cos(theta1+theta2),
        a1*np.sin(theta1)+a2*np.sin(theta1+theta2),
        d1 + theta3 + d4,
        theta1 + theta2 + theta4,
        0,
        0
    )

def ik(point: Point):

    x = point.x
    y = point.y
    z = point.z

    q3 = d1 + d4 - z
    if not (-0.45 <= q3 <= 0.0):
        return False
    
    try:
    
        q2 = np.arccos((x**2 + y**2 -a1**2 + a2**2) / (2*a1*a2))
        q2_1 = q2
        #q2_2 = -q2
        q1 = np.arctan(y/x) - np.arctan(a2*np.sin(q2_1) / a1 + a2*np.cos(q2_1))
        #q1_2 = np.arctan(y/x) - np.arctan(a2*np.sin(q2_2) / a1 + a2*np.cos(q2_2))
    except:
        return False

    if not (-2 <= q2 <= 2) or not (-2.5 <= q1 <= 2.55):
        return False

    return True

def plot() -> None:

    j1_space = np.linspace(-2.5, 2.5)
    j2_space = np.linspace(-2.0, 2.0)
    j3_space = np.linspace(0, 0.45)
    t1, t2 = np.meshgrid(j1_space, j2_space)

    x = a1*np.cos(t1)+a2*np.cos(t1+t2)
    y = a1*np.sin(t1)+a2*np.sin(t1+t2)

    data = []
    for i, value in enumerate(j3_space):
        if i%12 != 0:
            continue
        z = y*0+value
        data.append(go.Surface(z=z, x=x, y=y, colorscale='Blues', showscale=False, opacity=0.7))

    layout = go.Layout(scene = dict(xaxis = dict(title='X (m)'), yaxis = dict(title='Y (m)'), zaxis = dict(title='Z (m)'),),)

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig)

def callback(request: CheckTargetRequest) -> CheckTargetResponse : 

    return CheckTargetResponse(ik(request.target))

if __name__ == "__main__":

    try:
        rospy.init_node("homework_services_node", anonymous=True)
        rospy.loginfo("Starting services...")
        check_service = rospy.Service("/homework/check", CheckTarget, callback)
        plot()
        rospy.loginfo("Services started, spinning...")
        rospy.spin()

    except rospy.ROSInterruptException:
        pass
