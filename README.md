# Ponto Control - Sistema de controle de Ponto de Funcionários

<img align="center" alt="Python" width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"><span>&nbsp;&nbsp;&nbsp;</span>
<img align="center" alt="Django" width="50" src="https://cdn.worldvectorlogo.com/logos/django.svg"><span>&nbsp;&nbsp;&nbsp;</span>

## 📓Descrição

Este é um sistema desenvolvido em Django para gerenciar empresas, funcionários, pontos de entrada/saída e autenticação de usuários. O objetivo é oferecer um ambiente seguro e funcional para controle de registros de jornada de trabalho, associados a funcionários de diferentes empresas.

---

## ⚙Funcionalidades

### 🔒Autenticação e Permissões

- **Login**: Sistema de autenticação por CPF e senha.
- **Controle de Acesso**: Usuários são categorizados como superusuários ou usuários comuns.
- **Permissões Personalizadas**: Apenas usuários autenticados podem acessar funcionalidades restritas.

### 👔Empresas e Funcionários

- Cadastro e gerenciamento de empresas com informações básicas (nome e endereço).
- Cadastro de funcionários associados às empresas, incluindo CPF único e e-mail.
- Edição de dados de empresas e funcionários, inclusive com troca de senha de funcionários.
- Vinculação de usuários a funcionários.

### ⏱Controle de Ponto

- Registro de entrada e saída por funcionário.
- Cálculo automático de horas trabalhadas por dia.
- Filtragem de registros de ponto por intervalo de datas.

### 👨‍💼Interface do Administrador

- Customização da interface do Django Admin para gerenciar usuários e permissões com mais praticidade.

---

## 📚Estrutura do Projeto

### Aplicações

O projeto está dividido em aplicações modulares:

- **auth**: Gerenciamento de autenticação e login.
- **models**: Contém os modelos principais, como `Empresa`, `Funcionario`, `Usuario` e `Ponto`.
- **forms**: Validação de formulários, incluindo CPF e senhas.
- **views**: Controladores que lidam com a lógica de negócio e renderizam as páginas.
- **templates**: Interface com formulários, páginas de login e navegação dinâmica.

### Modelos Principais

- **Empresa**: Representa as empresas cadastradas no sistema.
- **Funcionario**: Associado a uma empresa, representa os colaboradores.
- **Usuario**: Gerenciado pela classe personalizada `UserManager` para autenticação baseada em CPF.
- **Ponto**: Registro de entrada e saída com cálculo de horas trabalhadas.

---

## Configuração e Execução

### Pré-requisitos

1. **Python 3.10+**
2. **Django 5.0+**
3. Banco de dados configurado (ex.: PostgreSQL). Para rodar localmente o SQLite serve muito bem e já está configurado.

### Passos para Configuração

1. Clone este repositório:

   ```bash
   git clone https://github.com/soareslucas9090/PontoControl-JM-TesteTecnico.git
   cd PontoControl-JM-TesteTecnico
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Aplique as migrações:

   ```bash
   python manage.py migrate
   ```

   **As migrações também iram criar os dados pré configurados para facilitar o teste do sistema. A tabela de usuários estará logo abaixo.**

5. Crie um superusuário:

   ```bash
   python manage.py createsuperuser
   ```

   **Não é necessário a criação do Super Usuário, por estar contido nos dados mockados, mas é possível a criação caso preferível.**

6. Colete os arquivos estáticos para disposição do servidor:

   ```bash
   python manage.py collectstatic
   ```

7. Inicie o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

---

## 📋Dados para Testes

Usando o `apps.py` foi criado uma mockagem de dados de Empresas, Funcionários, Pontos e Usuários, para facilitar os testes do sistema. Os dados são mockados após o primeiro migrate.

Foi inserido duas batidas de ponto para cada funcionário para o dia 02/01/2025 e dia 03/01/2025. Usar este intervalo no filtro de data para observar o histórico de pontos, ou iniciar um novo ponto.

| Nome           | Login       | Senha       | Email                   | Empresa    | Observação    |
| -------------- | ----------- | ----------- | ----------------------- | ---------- | ------------- |
| Admin          | 12345678910 | 12345678910 |                         |            | Superusuário  |
| Carlos Eduardo | 22222222222 | 12345678    | carlos.eduardo@emp1.com | DIS Matriz | Usuário comum |
| Maria Lúcia    | 33333333333 | 12345678    | maria.lucia@emp1.com    | DIS Matriz | Usuário comum |
| Antonio Soares | 44444444444 | 12345678    | antonio.soares@emp1.com | DIS Matriz | Usuário comum |
| Eduarda Soares | 55555555555 | 12345678    | eduarda.soares@emp2.com | DIS FL 01  | Usuário comum |
| Joel Menezes   | 66666666666 | 12345678    | joel.menezes@emp2.com   | DIS FL 01  | Usuário comum |

## 💻Documentação de Código

### **`models.py`**

- Define as classes principais do sistema, incluindo regras de validação e métodos personalizados como `horas_trabalhadas` para o modelo `Ponto`.

### **`forms.py`**

- Gerencia validações e formulários como CPF numérico e senhas seguras.

### **`views.py`**

- Contém as classes para autenticação, redirecionamento e proteção de rotas.

### **`admin.py`**

- Configura o Django Admin para exibir e editar registros com campos personalizados.

### **`urls.py`**

- Contem a configuração das rotas e urls do sistema.

### **`apps.py`**

- Contem a configuração do tipo de dado padrão de identificação de tabelas e a mockagem de dados.

---

## 🌐Páginas e Navegação

### Rotas Principais

- **`/`**: Página de redirecionamento dinâmica.
- **`/login/`**: Página de login.
- **`/admin/`**: Interface administrativa do Django.
- **`/menu/`**: Redirecionamento inical para superusuários.
- **`/pontos/`**: Redirecionamento para visualização de pontos de usuários comuns.

---
