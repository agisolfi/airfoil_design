import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os

"""
GOAL: FIND THE IDEAL NACA 4 DIGIT AIRFOIL DESIGN THAT PRODUCES THE GREATEST LIFT/DRAG RATIO. 

CONSTANTS:
RE= 1E6
AOA: 6

PARAMETERS TO OPTIMIZE

MAX CAMBER [FIRST DECIMAL]: VALUES BETWEEN 0 AND 9
POSITION OF MAX CAMBER [SECOND DECIMAL]: VALUES BETWEEN 0-9
MAX THICKNESS[3RD AND 4TH DECIMAL]: VALUES BETWEEN 10-40

"""


CAMBER=[0,1,2,3,4,5,6,7,8,9]
POSITION=[0,1,2,3,4,5,6,7,8,9]
THICKNESS=[10,15,20,25,30,35,40]
RESULTS=[]


def clean_slate():
    if os.path.exists("polar.txt"):
        os.remove("polar.txt")

def run_xfoil_script(airfoil):
    xfoil_commands = f"""
NACA {airfoil}
PANE
OPER
VISC 1000000
PACC
polar.txt

ALFA 6

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


    filename='polar.txt'
    cl, cd = 0,0
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
                        # alpha = float(parts[0])
                        cl = float(parts[1])
                        cd = float(parts[2])
                    except ValueError:
                        continue  # Skip malformed lines

    if(cd>0):
        ratio = cl/cd
    else:
        ratio=cl
    datapoint=[airfoil,ratio]
    print(datapoint)
    RESULTS.append(datapoint)

    
    
    
def plot_results():
    #order by most efficent airfoils
    RESULTS.sort(key=lambda x: x[1], reverse=True)

    BEST_AIRFOILS = RESULTS[:5]

    #have to unpack the tuple
    airfoils = [name for name, ld in BEST_AIRFOILS]
    ld_ratios = [ld for name, ld in BEST_AIRFOILS]

    plt.figure(figsize=(10, 6))
    plt.barh(airfoils,ld_ratios, color="skyblue")
    plt.ylabel('AIRFOIL DESIGN')
    plt.xlabel('L/D RATIO')
    plt.title('OPTIMIZATION OF NACA AIRFOILS AT RE 1E6 AND AOA 6')
    plt.gca().invert_yaxis()
    plt.grid(True,axis='x')
    plt.tight_layout()
    plt.show()




if __name__=="__main__":
    for c in CAMBER:
        for p in POSITION:
            for t in THICKNESS:
                naca_airfoil=str(c)+str(p)+str(t)
                clean_slate()
                run_xfoil_script(airfoil=naca_airfoil)
    plot_results()

