r"""Rotation helpers for the DOF scripts (imported, not run). Transform2 ArrayData: [0:3] part X, [3:6] Y, [6:9] Z in world."""
import math


def mat(a): return [[a[0], a[3], a[6]], [a[1], a[4], a[7]], [a[2], a[5], a[8]]]
def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def tr(A): return [list(r) for r in zip(*A)]
def rz(t): return [[math.cos(t), -math.sin(t), 0.0], [math.sin(t), math.cos(t), 0.0], [0.0, 0.0, 1.0]]


def axis_angle(R):
    c = max(-1.0, min(1.0, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)); th = math.acos(c)
    if th < 1e-9: return [0.0, 0.0, 0.0], 0.0
    v = [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]]; n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [round(x / n, 4) for x in v], math.degrees(th)


def rot_world_z(a, t):
    R = mm(rz(t), mat(a)); p = [sum(rz(t)[i][k] * a[9 + k] for k in range(3)) for i in range(3)]
    return [R[0][0], R[1][0], R[2][0], R[0][1], R[1][1], R[2][1], R[0][2], R[1][2], R[2][2], p[0], p[1], p[2]] + list(a[12:16])


def turned(a, b):
    """Rotation of transform a relative to b: about world Z for Z-axis parts; orbit + own-axis spin for the rest."""
    D = mm(mat(a), tr(mat(b)))
    shift = round(max(abs(a[9 + k] - b[9 + k]) for k in range(3)) * 1000.0, 4)
    if abs(b[8]) > 0.999:
        return f"turned {math.degrees(math.atan2(D[1][0], D[0][0])):8.4f} about Z{'' if abs(D[2][2] - 1) < 1e-9 else ' (NOT pure Z)'} | shift {shift}"
    ax0, ax1 = b[6:9], a[6:9]
    orbit = math.degrees(math.atan2(ax0[0] * ax1[1] - ax0[1] * ax1[0], ax0[0] * ax1[0] + ax0[1] * ax1[1]))
    axr, spin = axis_angle(mm(rz(-math.radians(orbit)), D))
    return f"orbit {orbit:8.4f} | spin {spin:8.4f} about {axr} | shift {shift}"
