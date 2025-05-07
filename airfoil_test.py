import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os

def clean_slate():
    if os.path.exists("polar.txt"):
        os.remove("polar.txt")

def run_xfoil_script(airfoil="2412", visc="1000000", aoa_start="0", aoa_end="12", aoa_step="1"):
    xfoil_commands = f"""
NACA {airfoil}
PSAV
naca2412_coords.dat
PANE
OPER
VISC {visc}
CPWR
cp_data.txt
PACC
polar.txt

ASEQ {aoa_start} {aoa_end} {aoa_step}

QUIT
    """
    process = subprocess.run(
        ['xfoil.exe'],
        input=xfoil_commands,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.returncode == 0:
        print("✅ XFOIL finished successfully.")
    else:
        print("❌ XFOIL failed to run.")
        print(process.stdout)
        print(process.stderr)


def plot_polar(filename='polar.txt'):
    alpha, cl, cd = [], [], []
    data_started = False

    with open(filename, 'r') as f:
        for line in f:
            # Start reading only after the dashed header line
            if '------' in line:
                data_started = True
                continue

            if data_started and line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        alpha.append(float(parts[0]))
                        cl.append(float(parts[1]))
                        cd.append(float(parts[2]))
                    except ValueError:
                        continue  # Skip malformed lines

    plt.figure(figsize=(8, 5))
    plt.plot(alpha, cl, marker='o', label='Cl vs AoA')
    plt.plot(alpha, cd, marker='o', label='Cd vs AoA')
    plt.xlabel('Angle of Attack (°)')
    plt.ylabel('Coefficent')
    plt.title('Lift/Drag Curve')
    plt.grid(True)
    plt.legend()
    plt.show()


def load_airfoil(filename):
    coords = np.loadtxt(filename, skiprows=1)
    return coords[:, 0], coords[:, 1]

def panel_geometry(x, y):
    N = len(x) - 1
    xc = 0.5 * (x[:-1] + x[1:])
    yc = 0.5 * (y[:-1] + y[1:])
    dx = x[1:] - x[:-1]
    dy = y[1:] - y[:-1]
    length = np.sqrt(dx**2 + dy**2)
    beta = np.arctan2(dy, dx)
    return xc, yc, length, beta

def build_matrix(xc, yc, x, y, beta):
    N = len(xc)
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i == j:
                A[i, j] = 0.5
            else:
                dx = xc[i] - x[j]
                dy = yc[i] - y[j]
                r_sq = dx**2 + dy**2
                A[i, j] = (1 / (2 * np.pi)) * (
                    np.sin(beta[i] - np.arctan2(dy, dx)) / r_sq
                )
    return A

def solve_gamma(A, alpha, beta):
    N = len(beta)
    RHS = -np.cos(beta - alpha)
    gamma = np.linalg.solve(A, RHS)
    return gamma

def compute_velocity_field(xc, yc, gamma, x_bounds, y_bounds, alpha):
    X, Y = np.meshgrid(np.linspace(*x_bounds, 200),
                       np.linspace(*y_bounds, 200))
    u = np.full_like(X, np.cos(alpha))
    v = np.full_like(Y, np.sin(alpha))

    for i in range(len(xc)):
        dx = X - xc[i]
        dy = Y - yc[i]
        r_sq = dx**2 + dy**2
        u += -gamma[i] * dy / (2 * np.pi * r_sq)
        v += gamma[i] * dx / (2 * np.pi * r_sq)

    return X, Y, u, v

def vortex_panel_plot(filename, alpha_deg):
    alpha = np.radians(alpha_deg)
    x, y = load_airfoil(filename)

    # Ensure it's a closed loop
    if not (x[0] == x[-1] and y[0] == y[-1]):
        x = np.append(x, x[0])
        y = np.append(y, y[0])

    xc, yc, _, beta = panel_geometry(x, y)
    A = build_matrix(xc, yc, x[:-1], y[:-1], beta)
    gamma = solve_gamma(A, alpha, beta)

    X, Y, u, v = compute_velocity_field(xc, yc, gamma, (-1.5, 2.5), (-1.5, 1.5), alpha)

    plt.figure(figsize=(10, 5))
    plt.streamplot(X, Y, u, v, color='steelblue', density=2)
    plt.fill(x, y, 'k', label='Airfoil')
    plt.title(f"Streamlines Around Airfoil at α = {alpha_deg}°")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.axis("equal")
    plt.grid(True)
    plt.legend()
    plt.show()



if __name__=="__main__":
    clean_slate()
    run_xfoil_script(airfoil="2412", visc="1000000", aoa_start="0", aoa_end="12", aoa_step="1")
    plot_polar()
    # vortex_panel_plot("naca2412_coords.dat", alpha_deg=5)
