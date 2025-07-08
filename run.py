import subprocess
import time
import os
import sys
import signal

processes = []

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
    
    # Backend
    print("\n[1/2] Iniciando API backend (porta 5000)...")
    backend_cmd = [sys.executable, "app.py"]
    backend = subprocess.Popen(backend_cmd, cwd="backend/api")
    processes.append(backend)
    
    # Aguardar um pouco
    print("\n[2/2] Aguardando 3 segundos...")
    time.sleep(3)
    
    # Frontend
    print("Iniciando frontend (porta 3000)...")
    frontend_cmd = [sys.executable, "app.py"]
    frontend = subprocess.Popen(frontend_cmd, cwd="frontend")
    processes.append(frontend)
    
    print("\nServidores iniciados!")
    print("Backend: http://localhost:5000")
    print("Frontend: http://localhost:3000")
    print("\nPressione Ctrl+C para parar os servidores...")
    
    try:
        # Aguardar até que um dos processos termine
        while True:
            time.sleep(1)
            for p in processes:
                if p.poll() is not None:
                    print(f"\nUm servidor parou inesperadamente.")
                    cleanup()
    except KeyboardInterrupt:
        cleanup()