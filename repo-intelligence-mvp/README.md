# Repository Intelligence MVP

Ferramenta local para analisar repositórios GitHub usando somente software aberto/local:
- Git para importar o repositório
- Python + FastAPI para a aplicação
- análise estática com Python AST e heurísticas para outras linguagens
- Ollama para inferência local
- Qwen3 4B como modelo padrão
- relatório Markdown com cobertura, evidências, arquitetura, stack, funcionalidades e possíveis problemas

## 1. Pré-requisitos

Windows 11 / Linux / macOS:

1. Git instalado e disponível no PATH.
2. Python 3.11+.
3. Ollama instalado.
4. Modelo baixado:

```bash
ollama pull qwen3:4b
```

Teste:

```bash
ollama run qwen3:4b
```

A aplicação usa `http://127.0.0.1:11434` por padrão.

## 2. Instalação

No terminal, dentro desta pasta:

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Se o PowerShell bloquear scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 3. Rodar

Com o ambiente virtual ativo:

```bash
uvicorn app.main:app --reload
```

Abra:

http://127.0.0.1:8000

Também existe documentação automática da API:

http://127.0.0.1:8000/docs

## 4. Uso

Informe uma URL pública do GitHub, por exemplo:

```text
https://github.com/seu-usuario/seu-repositorio
```

A tela de acompanhamento mostra, em tempo real:
- em qual das 6 etapas a análise está (Ollama → Clone → Inventário → Arquivos → Síntese → Concluído), com um indicador visual de progresso;
- quantos arquivos já foram processados e quantos faltam;
- quais arquivos estão sendo analisados neste momento;
- tempo decorrido e **tempo estimado restante (ETA)**, recalculado continuamente com base no ritmo real de chamadas ao modelo;
- ritmo de processamento (chamadas ao modelo por minuto);
- linguagens detectadas no repositório.

A análise executa:

1. validação/normalização da URL;
2. clone local (raso, um commit, um branch);
3. inventário de arquivos;
4. detecção de linguagens;
5. análise estrutural de Python;
6. extração de funções/classes/imports;
7. leitura de arquivos de documentação e configuração;
8. divisão do código em blocos;
9. análise de cada bloco pelo modelo (arquivos que cabem em um único bloco pulam direto para a análise consolidada, em uma única chamada);
10. consolidação por arquivo;
11. consolidação do projeto;
12. geração do relatório;
13. cálculo da cobertura de arquivos.

O relatório fica em:

```text
workspace/reports/<id>/report.md
```

Os dados intermediários ficam em:

```text
workspace/runs/<id>/
```

## 5. Importante sobre "analisar tudo"

O MVP tenta processar todos os arquivos de texto elegíveis, mas não envia o repositório inteiro em uma única chamada ao modelo.

Ele faz análise hierárquica:

```text
repositório
  -> inventário
  -> arquivo
  -> blocos de código
  -> resumo por arquivo
  -> síntese do projeto
  -> relatório
```

Isso é necessário para que um modelo de 4B consiga trabalhar com repositórios maiores.

Arquivos binários, diretórios de dependências/build/cache e arquivos acima do limite configurado são excluídos e aparecem no relatório como ignorados.

## 6. Configuração

Edite `.env`:

```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:4b

MAX_REPO_SIZE_MB=300
MAX_FILE_SIZE_KB=500
MAX_CHUNK_CHARS=10000
MAX_FILES=1000

WORKSPACE_DIR=workspace
REQUEST_TIMEOUT_SECONDS=300
OLLAMA_KEEP_ALIVE=5m

OLLAMA_THINK=false
OLLAMA_MAX_RETRIES=2
OLLAMA_RETRY_BACKOFF_SECONDS=3
MAX_SYNTHESIS_CHARS=60000
OLLAMA_CONCURRENCY=1
```

Para testar mais rápido em um projeto pequeno, reduza `MAX_CHUNK_CHARS`.

- `OLLAMA_THINK`: alguns modelos (como o Qwen3) têm um modo de "raciocínio" que,
  se ligado, produz blocos `<think>...</think>` na resposta. Por padrão isso
  fica desligado para manter o relatório limpo; qualquer bloco desse tipo que
  ainda vier do modelo é removido automaticamente como salvaguarda.
- `OLLAMA_MAX_RETRIES` / `OLLAMA_RETRY_BACKOFF_SECONDS`: número de novas
  tentativas e o intervalo entre elas quando uma chamada ao Ollama falha por
  motivo transitório (rede, timeout), para não derrubar a análise inteira por
  uma falha pontual.
- `MAX_SYNTHESIS_CHARS`: limite de caracteres agregados de resumos enviados
  de uma vez ao modelo nas etapas de consolidação (por arquivo e do projeto).
  Evita estourar a janela de contexto de um modelo pequeno em repositórios
  com muitos arquivos; o que não couber fica sinalizado no relatório.
- `OLLAMA_CONCURRENCY`: número de arquivos analisados em paralelo (padrão `1`,
  ou seja, sequencial — o mesmo comportamento de antes). Só aumente isso se o
  seu servidor Ollama realmente processa requisições em paralelo (ver
  `OLLAMA_NUM_PARALLEL` na documentação do Ollama e a capacidade da sua GPU);
  em uma instalação local comum, com um único modelo carregado, aumentar esse
  valor tende a enfileirar as chamadas do mesmo jeito e não traz ganho real.

## 7. Desempenho

Otimizações já aplicadas para manter a análise leve e rápida:

- **Uma chamada por arquivo pequeno, não duas.** Arquivos que cabem em um
  único bloco (a maioria de um repositório típico, dado `MAX_CHUNK_CHARS`)
  vão direto para a análise consolidada, sem uma etapa extra de
  "resumir o resumo".
- **Conexão HTTP reaproveitada** com o Ollama (pool com keep-alive), em vez
  de abrir uma conexão TCP nova a cada chamada.
- **Clone raso e leve**: `--depth 1 --single-branch --no-tags`, evitando
  baixar histórico, outros branches e tags.
- **Leitura de binários em streaming**: a checagem de "isto é um arquivo
  binário?" lê só os primeiros 4 KB do arquivo, em vez de carregar o
  arquivo inteiro na memória.
- **Orçamento de contexto** (`MAX_SYNTHESIS_CHARS`) para não estourar a
  janela de um modelo pequeno em repositórios com muitos arquivos.
- **Paralelismo opcional** (`OLLAMA_CONCURRENCY`) para quando o backend do
  modelo suporta múltiplas requisições simultâneas.

## 8. API

### POST /api/analyze

```json
{
  "url": "https://github.com/usuario/projeto"
}
```

Retorna o ID da execução.

### GET /api/runs

Lista todas as execuções desta sessão do servidor (id, URL, status, etapa).

### GET /api/runs/{run_id}

Retorna o status.

### GET /api/runs/{run_id}/report

Retorna o Markdown do relatório.

## 9. Testes

Testes automatizados cobrem o scanner (detecção de linguagem, arquivos
binários, inventário) e as funções auxiliares do pipeline (validação de URL,
divisão em blocos, orçamento de contexto na síntese):

```bash
pip install -r requirements-dev.txt
pytest
```

## 10. Limitações atuais

Este é um MVP.

Ainda não possui:
- banco vetorial;
- embeddings;
- GraphRAG;
- análise profunda de todas as linguagens via AST;
- execução de testes do projeto analisado;
- análise dinâmica;
- autenticação GitHub;
- suporte a repositórios privados;
- interface de perguntas e respostas sobre o repositório.

Esses recursos devem entrar em etapas posteriores.

## 11. Próxima evolução

A arquitetura foi pensada para evoluir para:

```text
GitHub
  |
  v
Repository Ingestion
  |
  +--> Static Analysis
  |      +--> AST
  |      +--> imports
  |      +--> functions/classes
  |      +--> dependency graph
  |
  +--> Documentation
  |
  +--> Code chunks
          |
          v
     Embeddings
          |
          v
      Vector DB
          |
          +------> Graph
                    |
                    v
                  Agent
                    |
                    v
                Evidence
                    |
                    v
                 Report
```

O objetivo acadêmico pode ser transformar vários repositórios de projetos em uma base de conhecimento técnico consultável por IA.
