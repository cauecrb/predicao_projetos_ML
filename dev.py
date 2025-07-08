import os
import sys

def main():
    choice = input("Escolha uma opção:\n1 - Só backend\n2 - Só frontend\n3 - Ambos\n> ")
    
    if choice == "1":
        print("Iniciando backend...")
        os.chdir("backend/api")
        os.system(f"{sys.executable} app.py")
    
    elif choice == "2":
        print("Iniciando frontend...")
        os.chdir("frontend")
        os.system(f"{sys.executable} app.py")
    
    elif choice == "3":
        print("Iniciando ambos...")
        os.system(f"{sys.executable} run.py")
    
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()