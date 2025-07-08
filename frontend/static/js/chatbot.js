class ChatbotAPI {
    constructor() {
        this.baseURL = 'http://localhost:3000/api';
    }

    async predict(projectData) {
        try {
            const response = await fetch(`${this.baseURL}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(projectData)
            });
            
            return await response.json();
        } catch (error) {
            console.error('Erro na predição:', error);
            return { erro: 'Erro de comunicação com a API' };
        }
    }

    async getUsers() {
        try {
            const response = await fetch(`${this.baseURL}/users`);
            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar usuários:', error);
            return { erro: 'Erro de comunicação com a API' };
        }
    }
}

// Instância global
const chatbotAPI = new ChatbotAPI();