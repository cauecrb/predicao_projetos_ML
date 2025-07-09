import subprocess
import time
import os
import sys
import signal
import platform

processes = []

def activate_venv():
    print("\nVerificando ambiente virtual...")
    
    if platform.system() == "Windows":
        venv_script = "venv\\Scripts\\activate.bat"
        if os.path.exists(venv_script):
            print("Ambiente virtual encontrado (Windows).")
            return True
    else:
        venv_script = "venv/bin/activate"
        if os.path.exists(venv_script):
            print("Ambiente virtual encontrado (Linux/Mac).")
            return True
    
    print("AVISO: Ambiente virtual não encontrado em venv/")
    return False

def get_python_cmd():
    if activate_venv():
        if platform.system() == "Windows":
            return "venv\\Scripts\\python.exe"
        else:
            return "venv/bin/python"
    return sys.executable

def cleanup():
    print("\nParando servidores...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=5)
        except:
            try:
                p.kill()
            except:
                pass
    print("Servidores parados.")
    sys.exit(0)

def signal_handler(sig, frame):
    cleanup()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    print("Iniciando servidores...")
    
    python_cmd = get_python_cmd()
    
    # Backend
    print("\n[1/2] Iniciando API backend (porta 5000)...")
    backend_cmd = [python_cmd, "app.py"]
    backend = subprocess.Popen(backend_cmd, cwd="backend/api")
    processes.append(backend)
    
    # Aguardar um pouco
    print("\n[2/2] Aguardando 3 segundos...")
    time.sleep(3)
    
    # Frontend
    print("Iniciando frontend (porta 3000)...")
    frontend_cmd = [python_cmd, "app.py"]
    frontend = subprocess.Popen(frontend_cmd, cwd="frontend")
    processes.append(frontend)
    
    print("\nServidores iniciados!")
    print("Backend: http://localhost:5000")
    print("Frontend: http://localhost:3000")
    print("\nPressione Ctrl+C para parar os servidores...")
    
    try:
        while True:
            time.sleep(1)
            for p in processes:
                if p.poll() is not None:
                    print(f"\nUm servidor parou inesperadamente.")
                    cleanup()
    except KeyboardInterrupt:
        cleanup()