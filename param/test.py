import numpy as np
from numpy import exp, sqrt
import matplotlib.pyplot as plt


def meshgrid3D(x, y, z):
    """A slimmed-down version of http://www.scipy.org/scipy/numpy/attachment/ticket/966/meshgrid.py"""
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)
    z_arr = np.asarray(z)
    return np.meshgrid(x_arr, y_arr, z_arr, indexing='ij')

def stRF_2d(x: np.ndarray, y: np.ndarray, t: np.ndarray, p) -> np.ndarray:
    """
    Spatiotemporal receptive field model.
    Args:
        x, y, t: 3D arrays from meshgrid3D.
        p: Parameters object.
    Returns:
        rf: Receptive field output (3D array).
    """
    tmc = G(t, p.K1, p.K2, p.c1, p.c2, p.t1, p.t2, p.n1, p.n2)
    tms = G(t - p.td, p.K1, p.K2, p.c1, p.c2, p.t1, p.t2, p.n1, p.n2)

    fcm = F_2d(x, y, p.Ac, p.sigma_c)
    fsm = F_2d(x, y, p.As, p.sigma_s)

    rf = fcm * tmc - fsm * tms

    # Validate areas
    x_res = x[1, 0, 0] - x[0, 0, 0]
    fcm_area = fcm[:, :, 0].sum() * x_res ** 2
    center_area = 2 * np.pi * p.sigma_c ** 2 * p.Ac
    assert abs(fcm_area - center_area) / max(fcm_area, center_area) < 0.01, (
        f"Synthesized center of RF doesn't fit the supplied sigma and amplitude "
        f"({fcm_area:.6f}-{center_area:.6f}={abs(fcm_area - center_area):.6f}), "
        "check visual field size and model size!"
    )

    fsm_area = fsm[:, :, 0].sum() * x_res ** 2
    surround_area = 2 * np.pi * p.sigma_s ** 2 * p.As
    assert abs(fsm_area - surround_area) / max(fsm_area, surround_area) < 0.01, (
        f"Synthesized surround of RF doesn't fit the supplied sigma and amplitude "
        f"({fsm_area:.6f}-{surround_area:.6f}={abs(fsm_area - surround_area):.6f}), "
        "check visual field size and model size!"
    )

    if p.subtract_mean:
        for i in range(rf.shape[2]):  # Normalize each time slice
            rf[:, :, i] -= rf[:, :, i].mean()

    return rf




def G(t: np.ndarray, K1: float, K2: float, c1: float, c2: float, 
      t1: float, t2: float, n1: float, n2: float) -> np.ndarray:
    """Temporal component of the receptive field."""
    p1 = K1 * ((c1 * (t - t1)) ** n1 * exp(-c1 * (t - t1))) / ((n1 ** n1) * exp(-n1))
    p2 = K2 * ((c2 * (t - t2)) ** n2 * exp(-c2 * (t - t2))) / ((n2 ** n2) * exp(-n2))
    return p1 - p2


def F_2d(x: np.ndarray, y: np.ndarray, A: float, sigma: float) -> np.ndarray:
    """Spatial component of the receptive field."""
    return A * exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2))


# Create a simple parameter class
class Parameters:
    def __init__(self):
        # original AllenFreeman2006, with Linsenmeier et al. 1982
        self.K1 = 1*1.05  # transient height
        self.c1 = 0.14/1  # AllenFreeman2006
        self.n1 = 7.0  # transient center
        self.t1 = -6.0  # transient offset (ms)
        self.K2 = 1*0.7  # AllenFreeman2006
        self.c2 = 0.12  # AllenFreeman2006
        self.n2 = 8.0  # AllenFreeman2006
        self.t2 = -0.6  # sustained offset (ms)
        self.Ac = 1.0  # example value
        self.As = 0.7  # example value
        self.sigma_c = 1.0  # example value
        self.sigma_s = 2.0  # example value
        self.td = 0.0  # example value
        self.subtract_mean = False


# Main code
if __name__ == "__main__":
    p = Parameters()
    time_points = np.arange(300)
    vals = [G(t, p.K1, p.K2, p.c1, p.c2, p.t1, p.t2, p.n1, p.n2) for t in time_points]

    plt.figure()
    plt.xlabel('Time (ms)')
    plt.ylabel('Response')
    plt.plot(time_points, vals, '-')
    plt.savefig('temporal.png')
    plt.show()