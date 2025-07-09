import os
import sys
import platform

def get_python_cmd():
    if platform.system() == "Windows":
        if os.path.exists("venv\\Scripts\\python.exe"):
            return "venv\\Scripts\\python.exe"
    else:
        if os.path.exists("venv/bin/python"):
            return "venv/bin/python"
    return sys.executable

def main():
    python_cmd = get_python_cmd()
    
    if "venv" in python_cmd:
        print("Usando ambiente virtual.")
    else:
        print("AVISO: Ambiente virtual não encontrado, usando Python do sistema.")
    
    choice = input("\nEscolha uma opção:\n1 - Só backend\n2 - Só web chatbot\n3 - Ambos\n> ")
    
    if choice == "1":
        print("Iniciando backend...")
        os.chdir("backend/api")
        os.system(f"{python_cmd} app.py")
    
    elif choice == "2":
        print("Iniciando web chatbot...")
        os.chdir("chat_bot/chatbot")
        os.system(f"{python_cmd} web_chatbot.py")
    
    elif choice == "3":
        print("Iniciando ambos...")
        os.system(f"{python_cmd} run.py")
    
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()