import subprocess
import matplotlib.pyplot as plt

def run_xfoil_script():
    # Input script as a multiline string
    xfoil_commands = """
NACA 2412
PANE
OPER
VISC 1000000
PACC
polar.txt


ASEQ 0 12 1
QUIT
    """

    # Start the XFOIL subprocess
    process = subprocess.run(
        ['xfoil.exe'], 
        input=xfoil_commands,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Output handling
    if process.returncode == 0:
        print("✅ XFOIL finished successfully.")
    else:
        print("❌ XFOIL failed to run.")
        print(process.stdout)
        print(process.stderr)

def plot_polar(filename='polar.txt'):
    alpha = []
    cl = []
    cd = []

    with open(filename, 'r') as f:
        lines = f.readlines()

        for line in lines:
            if line.strip() and line[0].isdigit() or line[0] == '-':
                parts = line.split()
                if len(parts) >= 3:
                    alpha.append(float(parts[0]))
                    cl.append(float(parts[1]))
                    cd.append(float(parts[2]))

    plt.figure(figsize=(8, 5))
    plt.plot(alpha, cl, label='Cl')
    plt.xlabel('Angle of Attack (°)')
    plt.ylabel('Lift Coefficient (Cl)')
    plt.title('Lift Curve')
    plt.grid(True)
    plt.legend()
    plt.show()



if __name__ == "__main""":
    run_xfoil_script()
    plot_polar()


