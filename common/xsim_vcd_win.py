import os
import sys
import shutil
import subprocess

def modify_tcl(tcl_path, tcl_vcd_path):
    with open(tcl_path, 'r') as f:
        lines = f.readlines()

    # Insert VCD commands before log_wave
    for i, line in enumerate(lines):
        if 'log_wave -r /' in line:
            lines = lines[:i] + ['open_vcd\n', 'log_vcd *\n'] + lines[i:]
            break

    # Replace final lines
    for i in range(len(lines)):
        if lines[i].strip() == 'run all' and i + 1 < len(lines) and lines[i + 1].strip() == 'quit':
            lines[i + 1] = 'close_vcd\nquit\n'
            break

    with open(tcl_vcd_path, 'w') as f:
        f.writelines(lines)

def create_vcd_batch(original_bat, new_bat):
    with open(original_bat, 'r') as f:
        for line in f:
            if 'xsim' in line:
                xsim_line = line.replace('add.tcl', 'add_vcd.tcl')
                break
        else:
            raise RuntimeError("No xsim line found in batch file.")

    with open(new_bat, 'w') as f:
        f.write('cd /d "%~dp0"\n')
        f.write(xsim_line)

def run_batch(batch_path):
    subprocess.run(batch_path, shell=True, check=True)

def copy_vcd(sim_dir, base_dir, component_path):
    src = os.path.join(sim_dir, 'dump.vcd')
    if not os.path.exists(src):
        print("⚠️ dump.vcd not found.")
        return

    vcd_dir = os.path.join(base_dir, 'vcd')
    os.makedirs(vcd_dir, exist_ok=True)

    safe_name = component_path.replace(os.sep, '_')
    dst = os.path.join(vcd_dir, f'{safe_name}_dump.vcd')
    shutil.copyfile(src, dst)
    print(f"✅ VCD copied to {dst}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_xsim_vcd.py scalar_add/add")
        sys.exit(1)

    component_path = sys.argv[1]
    base_dir = os.getcwd()
    sim_dir = os.path.join(base_dir, component_path, 'hls', 'sim', 'verilog')

    tcl_path = os.path.join(sim_dir, 'add.tcl')
    tcl_vcd_path = os.path.join(sim_dir, 'add_vcd.tcl')
    bat_path = os.path.join(sim_dir, 'run_xsim.bat')
    bat_vcd_path = os.path.join(sim_dir, 'run_xsim_vcd.bat')

    if not os.path.exists(sim_dir):
        raise FileNotFoundError(f"Simulation directory not found: {sim_dir}")

    modify_tcl(tcl_path, tcl_vcd_path)
    create_vcd_batch(bat_path, bat_vcd_path)
    run_batch(bat_vcd_path)
    copy_vcd(sim_dir, base_dir, component_path)

if __name__ == "__main__":
    main()