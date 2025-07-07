import sys
import os
import pandas as pd
import joblib
import json
from datetime import datetime
import re
import webbrowser
import threading
import time
import platform
import subprocess

sys.path.append('../../ML/factory_data')
sys.path.append('../../ML/ml_model')

from model_forest import HybridProjectSuccessModel

#chatbot para acessar a api
class EnhancedProjectChatbot:
    
    def __init__(self):
        self.hybrid_model = HybridProjectSuccessModel()
        self.users_df = None
        self.current_project = {}
        self.current_user_profile = None
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_state = 'inicio'
        
        # Campos de perguntas do projeto
        self.project_questions = [
            {
                'field': 'Duracao_meses',
                'question': 'Duração do projeto em meses?',
                'validation': {'type': 'int', 'min': 1, 'max': 60},
                'tips': 'Projetos de 6-12 meses têm maior taxa de sucesso'
            },
            {
                'field': 'Orcamento_R$',
                'question': 'Orçamento total em reais? (1000 a 10000000)',
                'validation': {'type': 'float', 'min': 1000, 'max': 10000000},
                'tips': 'Orçamentos realistas aumentam as chances de sucesso'
            },
            {
                'field': 'Tamanho_da_Equipe',
                'question': 'Tamanho da equipe? (1 a 50 pessoas)',
                'validation': {'type': 'int', 'min': 1, 'max': 50},
                'tips': 'Equipes de 5-8 pessoas são mais eficientes'
            },
            {
                'field': 'RecursosDisponiveis',
                'question': 'Recursos disponíveis? (baixo/médio/alto)',
                'validation': {'type': 'choice', 'options': ['baixo', 'médio', 'alto']},
                'tips': 'Recursos adequados são fundamentais'
            }
        ]
        
        self.initialize_system()
    
    #inicializar o modelo
    def initialize_system(self):
        try:
            model_loaded = self.hybrid_model.load_model('../../ML/ml_model/trained_model.joblib')
            
            if not model_loaded:
                print("Modelo não encontrado. Tentando treinar...")
                success = self.hybrid_model.run_full_pipeline(
                    '../../ML/datas/projetos_fake_dataset.csv',
                    '../../ML/datas/usuarios_dataset.csv'
                )
                if not success:
                    print("Erro: Não foi possível inicializar o modelo")
                    return False
            
            # Carregar dados de usuários
            self.users_df = pd.read_csv('../../ML/datas/usuarios_dataset.csv')
            print(f"Sistema inicializado: {len(self.users_df)} usuários")
            return True
            
        except Exception as e:
            print(f"Erro na inicialização: {e}")
            return False
    
    #inicia conversa
    def start_conversation(self):

        print("\n" + "==========================================")
        print("ASSISTENTE DE ANÁLISE DE PROJETOS")
        print("===========================================")
        print("Análise de sucesso baseada em histórico de projetos.")
        print("\n-------------------------------")
        
        self.conversation_state = 'coletando_projeto'
        self.collect_project_information()
    

    #informaçoes fornecidade pelo usuario
    def collect_project_information(self):
        print("\nResponda sobre seu projeto:\n")
        
        for question_data in self.project_questions:
            success = self.ask_question(question_data)
            if not success:
                print("Análise cancelada.")
                return
        
        print("\nIdentificando seu perfil...")
        self.identify_user_profile()
    
    def ask_question(self, question_data):
        field = question_data['field']
        question = question_data['question']
        validation = question_data['validation']
        tips = question_data.get('tips', '')
        
        while True:
            if tips:
                print(f"\n{tips}")
            response = input(f"{question} ").strip()
            
            if response.lower() in ['sair', 'cancelar', 'parar']:
                return False
            
            is_valid, processed_value, error_msg = self.validate_response(response, validation)
            
            if is_valid:
                self.current_project[field] = processed_value
                print(f"{field}: {processed_value}")
                return True
            else:
                print(f"{error_msg}.  insira outro valor")
    
    #resposta do usuario
    def validate_response(self, response, validation):
        try:
            if validation['type'] == 'int':
                value = int(response)
                if validation['min'] <= value <= validation['max']:
                    return True, value, ""
                return False, None, f"Valor deve estar entre {validation['min']} e {validation['max']}"
            
            elif validation['type'] == 'float':
                clean_value = response.replace('R$', '').replace(' ', '')
                value = float(clean_value)
                if validation['min'] <= value <= validation['max']:
                    return True, value, ""
                return False, None, f"Valor deve estar entre R$ {validation['min']:,.2f} e R$ {validation['max']:,.2f}"
            
            elif validation['type'] == 'choice':
                value = response.lower().strip()
                if value in validation['options']:
                    return True, value, ""
                return False, None, f"Opções: {', '.join(validation['options'])}"
                
        except ValueError:
            return False, None, "Formato inválido"
        
        return False, None, "Erro de validação"
    
    def identify_user_profile(self):
        print("\nIDENTIFICAÇÃO DO PERFIL")
        print("Buscando seu perfil na base...\n")
        
        # Mostrar opções de cargo
        cargos_disponiveis = self.users_df['Cargo'].unique()
        print("Cargos disponíveis:")
        for i, cargo in enumerate(cargos_disponiveis, 1):
            count = len(self.users_df[self.users_df['Cargo'] == cargo])
            print(f"{i}. {cargo} ({count} usuários)")
        
        while True:
            try:
                choice = input("\nQual seu cargo? (número ou nome): ").strip()
                
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(cargos_disponiveis):
                        selected_cargo = cargos_disponiveis[idx]
                        break
                else:
                    # Busca por nome
                    matches = [c for c in cargos_disponiveis if choice.lower() in c.lower()]
                    if len(matches) == 1:
                        selected_cargo = matches[0]
                        break
                    elif len(matches) > 1:
                        print(f"Múltiplas opções encontradas: {', '.join(matches)}")
                        continue
                
                print("Opção inválida. Tente novamente.")
                
            except ValueError:
                print("Entrada inválida.")
        
        # Buscar usuários com esse cargo
        users_with_cargo = self.users_df[self.users_df['Cargo'] == selected_cargo]
        
        if len(users_with_cargo) == 1:
            self.current_user_profile = users_with_cargo.iloc[0]
        else:
            print(f"\nUsuários com cargo '{selected_cargo}':")
            for i, (_, user) in enumerate(users_with_cargo.iterrows(), 1):
                print(f"{i}. {user['Nome']} - {user['Experiencia(anos)']} anos - {user['Sucesso_Medio(percentual)']}% sucesso")
            
            while True:
                try:
                    choice = int(input("\nEscolha seu perfil (número): ")) - 1
                    if 0 <= choice < len(users_with_cargo):
                        self.current_user_profile = users_with_cargo.iloc[choice]
                        break
                    print("Número inválido.")
                except ValueError:
                    print("Digite um número válido.")
        
        print(f"\nPerfil identificado: {self.current_user_profile['Nome']}")
        print(f"   Experiência: {self.current_user_profile['Experiencia(anos)']} anos")
        print(f"   Sucesso histórico: {self.current_user_profile['Sucesso_Medio(percentual)']}%")
        
        self.generate_prediction()
    
    def generate_prediction(self):
        print("\nGERANDO ANÁLISE...")
        print("Processando dados...\n")
        
        project_data = self.current_project.copy()
        user_cargo = self.current_user_profile['Cargo']
        
        # Fazer predição
        result = self.hybrid_model.predict_single_project(project_data, user_cargo)
        
        if 'error' in result:
            print(f"Erro na análise: {result['error']}")
            return
        
        self.display_personalized_results(result)
        self.save_analysis_to_history(result)
    
    def display_personalized_results(self, prediction_result):
        prob_sucesso = prediction_result['success_probability']
        user_name = self.current_user_profile['Nome']
        user_exp = self.current_user_profile['Experiencia(anos)']
        user_success = self.current_user_profile['Sucesso_Medio(percentual)']
        
        print("=======================================")
        print("ANÁLISE DO PROJETO")
        print("=======================================")
        
        print(f"\nRESULTADO PARA {user_name.upper()}:")
        print(f"Probabilidade de sucesso: {prob_sucesso}%")
        
        if prob_sucesso >= 80:
            status_emoji = "🟢"
            status_text = "EXCELENTE POTENCIAL"
        elif prob_sucesso >= 60:
            status_emoji = "🟡"
            status_text = "BOM POTENCIAL COM ATENÇÃO"
        else:
            status_emoji = "🔴"
            status_text = "ALTO RISCO - REVISÃO NECESSÁRIA"
        
        print(f"\n{status_emoji} STATUS: {status_text}")
        
        print(f"\nSeu perfil: {user_exp} anos, {user_success}% sucesso histórico")
        
        # Análise dos fatores do projeto
        self.analyze_project_factors()
        self.generate_personalized_recommendations(prob_sucesso, user_exp, user_success)
        
        print("===================================")
    
    def analyze_project_factors(self):
        print(f"\nFATORES DO PROJETO:")
        
        # Análise do orçamento
        orcamento = self.current_project['Orcamento_R$']
        if orcamento < 100000:
            print(f"   Orçamento: R$ {orcamento:,.2f} - Abaixo da média dos projetos de sucesso")
            print(f"      Considere revisar o orçamento para aumentar as chances de sucesso")
        elif orcamento > 1000000:
            print(f"   Orçamento: R$ {orcamento:,.2f} - Bem acima da média")
            print(f"      Orçamento robusto, mas monitore os gastos de perto")
        else:
            print(f"   Orçamento: R$ {orcamento:,.2f} - Dentro da faixa adequada")
        
        # Análise da duração
        duracao = self.current_project['Duracao_meses']
        if duracao > 18:
            print(f"   Duração: {duracao} meses - Projeto longo, maior risco")
            print(f"      Considere dividir em fases menores")
        elif duracao < 3:
            print(f"   Duração: {duracao} meses - Projeto muito curto")
            print(f"      Verifique se o cronograma é realista")
        else:
            print(f"   Duração: {duracao} meses - Duração adequada")
        
        # Análise da equipe
        equipe = self.current_project['Tamanho_da_Equipe']
        if equipe > 15:
            print(f"   Equipe: {equipe} pessoas - Equipe grande")
            print(f"      Atenção especial à comunicação e coordenação")
        elif equipe < 3:
            print(f"   Equipe: {equipe} pessoas - Equipe pequena")
            print(f"      Verifique se há recursos suficientes")
        else:
            print(f"   Equipe: {equipe} pessoas - Tamanho adequado")
        
        # Análise dos recursos
        recursos = self.current_project['RecursosDisponiveis']
        if recursos == 'baixo':
            print(f"   Recursos: {recursos} - Pode impactar negativamente o projeto")
            print(f"      Considere aumentar os recursos ou reduzir o escopo")
        elif recursos == 'alto':
            print(f"   Recursos: {recursos} - Excelente disponibilidade")
        else:
            print(f"   Recursos: {recursos} - Nível adequado")
    
    def generate_personalized_recommendations(self, prob_sucesso, user_exp, user_success):
        print(f"\nRECOMENDAÇÕES:")
        
        # Recomendações baseadas na probabilidade
        if prob_sucesso >= 80:
            print("Projeto com excelente potencial")
            print("Prossiga com confiança")
        elif prob_sucesso >= 60:
            print("Projeto viável, monitore o andamento do projeto")
            print("Considere ajustes no planejamento")
        else:
            print("Projeto de alto risco")
            print("Revisão necessária")
        
        # Recomendações baseadas no perfil do usuário
        if user_exp < 3:
            print("Busque mentoria devido à pouca experiência")
        elif user_exp > 10:
            print("Use a experiência para mitigar riscos")
        
        if user_success < 60:
            print("Foque em melhorias baseadas no histórico")
        elif user_success > 80:
            print("Aplique suas melhores práticas")
        
        # Recomendações específicas do projeto
        orcamento = self.current_project['Orcamento_R$']
        if orcamento < 100000:
            print("Considere aumentar o orçamento")
        
        recursos = self.current_project['RecursosDisponiveis']
        if recursos == 'baixo':
            print(f"  Priorize aquisição de recursos adequados")
        
        duracao = self.current_project['Duracao_meses']
        if duracao > 12:
            print(f"  Considere dividir em marcos de 3-4 meses")
    
    def save_analysis_to_history(self, result):
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'user_profile': {
                'nome': self.current_user_profile['Nome'],
                'cargo': self.current_user_profile['Cargo'],
                'experiencia': self.current_user_profile['Experiencia(anos)'],
                'sucesso_historico': self.current_user_profile['Sucesso_Medio(percentual)']
            },
            'project_data': self.current_project.copy(),
            'prediction_result': result,
            'session_id': self.session_id
        }
        
        self.conversation_history.append(analysis)
    
    # executar chatbot
    def run(self):
        if not hasattr(self.hybrid_model, 'is_trained') or not self.hybrid_model.is_trained:
            print("Sistema não inicializado, Verifique se o modelo foi treinado.")
            return
        
        try:
            self.start_conversation()
            
            # Perguntar se quer fazer nova análise
            while True:
                print("\n" + "----------------------------")
                choice = input("\nDeseja analisar outro projeto? (s/n): ").strip().lower()
                
                if choice in ['s', 'sim', 'y', 'yes']:
                    self.current_project = {}
                    self.current_user_profile = None
                    print("\n" + "=======================================")
                    print("NOVA ANÁLISE")
                    print("=================================")
                    self.collect_project_information()
                elif choice in ['n', 'não', 'nao', 'no']:
                    print("\nSaindo...")
                    break
                else:
                    print("Resposta inválida. Digite 's' para sim ou 'n' para não.")
                    
        except KeyboardInterrupt:
            print("\n\nSaindo...")
        except Exception as e:
            print(f"\nErro inesperado aqui: {e}")

    #abrir o frontend no navegador, ele tambem verifica o sistema operacional ja que estou usando wsl
    def open_frontend(self):
        try:
            # Caminho para o arquivo HTML
            html_file = os.path.join(os.path.dirname(__file__), 'templates', 'chatbot_clean.html')
            
            if not os.path.exists(html_file):
                html_file = os.path.join(os.path.dirname(__file__), 'templates', 'chatbot.html')
            
            if os.path.exists(html_file):
                print(f"Abrindo: {html_file}")
                
                # Detecta o ambiente
                system = platform.system().lower()
                
                if system == 'windows':
                    os.startfile(html_file)
                elif 'microsoft' in platform.uname().release.lower():
                    windows_path = html_file.replace('/mnt/c/', 'C:\\')
                    windows_path = windows_path.replace('/', '\\')
                    subprocess.run(['cmd.exe', '/c', 'start', windows_path], check=True)
                elif system == 'darwin':
                    subprocess.run(['open', html_file], check=True)
                else:
                    try:
                        subprocess.run(['xdg-open', html_file], check=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        browsers = ['google-chrome', 'firefox', 'chromium-browser', 'chromium']
                        for browser in browsers:
                            try:
                                subprocess.run([browser, html_file], check=True)
                                break
                            except FileNotFoundError:
                                continue
                        else:
                            file_url = f"file:///{html_file.replace(os.sep, '/')}"
                            webbrowser.open(file_url)
                
                print("Frontend aberto no navegador!")
                return True
            else:
                print(f"HTML não encontrado: {html_file}")
                return False
                
        except Exception as e:
            print(f"Erro ao abrir frontend: {e}")
            return False
    
    def run_with_frontend(self):
        if not hasattr(self.hybrid_model, 'is_trained') or not self.hybrid_model.is_trained:
            print("Sistema não inicializado.")
            return
        
        print("ASSISTENTE DE ANÁLISE DE PROJETOS")
        print("========================================")
        print("Iniciando interface...")
        
        self.run()

if __name__ == "__main__":
    chatbot = EnhancedProjectChatbot()
    chatbot.run_with_frontend()