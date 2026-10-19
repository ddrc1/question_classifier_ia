# Question Classificator

Projeto para classificar questões usando LangGraph e modelos da OpenAI.

## Requisitos
- [uv](https://docs.astral.sh/uv/) para gerenciar o ambiente e as dependências
- Uma chave de API da OpenAI com acesso aos modelos configurados no projeto
- Credenciais do Langfuse para enviar os traces da execução

## Configuração

1. Instale o `uv`, caso ainda não esteja instalado:

   ```powershell
   irm https://astral.sh/uv/install.ps1 | iex
   ```

3. Crie um arquivo `.env` na raiz do projeto utilizando `.env.example` como exemplo.

## Executar

Execute os comandos a partir da raiz do repositório, pois os caminhos dos arquivos
de dados são relativos a essa pasta:

```
uv run python main.py
```
