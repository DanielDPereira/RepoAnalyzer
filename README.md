# Repository Analizer MVP

Ferramenta local para análise automatizada de repositórios GitHub usando **software aberto e inferência local**.

O projeto combina análise estática, processamento de arquivos e um modelo de linguagem executado pelo **Ollama** para produzir um relatório técnico sobre o repositório analisado.

A proposta é transformar um repositório de código em uma visão estruturada de sua **arquitetura, tecnologias, funcionalidades, evidências de implementação e possíveis problemas**.

## ✨ Funcionalidades

* Importação de repositórios públicos do GitHub.
* Clone raso para reduzir tempo e espaço utilizados.
* Inventário dos arquivos do projeto.
* Detecção automática de linguagens.
* Análise estrutural de Python usando `ast`.
* Extração de funções, classes e imports.
* Leitura de documentação e arquivos de configuração.
* Divisão de arquivos grandes em blocos.
* Análise de código utilizando um LLM local.
* Consolidação das análises por arquivo.
* Síntese geral do projeto.
* Geração automática de relatório em Markdown.
* Cálculo da cobertura de arquivos analisados.
* Acompanhamento da execução em tempo real.
* Estimativa dinâmica do tempo restante (ETA).
* Registro das etapas e dados intermediários de cada execução.
* Execução totalmente local, sem necessidade de API externa de IA.

### Stack

| Componente               | Tecnologia               |
| ------------------------ | ------------------------ |
| Backend                  | Python + FastAPI         |
| Análise estática         | Python AST + heurísticas |
| LLM                      | Ollama                   |
| Modelo padrão            | Qwen3 4B                 |
| Versionamento/importação | Git                      |
| Relatórios               | Markdown                 |
| Interface                | Web                      |

---

## 🏗️ Arquitetura

O pipeline principal segue uma abordagem hierárquica:

```text
GitHub Repository
       │
       ▼
 URL Validation
       │
       ▼
  Git Clone
       │
       ▼
   Inventory
       │
       ├── Language Detection
       ├── Static Analysis
       ├── Documentation
       └── Configuration
       │
       ▼
   Code Chunks
       │
       ▼
  Local LLM Analysis
       │
       ▼
 File-level Synthesis
       │
       ▼
Project-level Synthesis
       │
       ▼
    Report
```

Essa abordagem evita enviar um repositório inteiro em uma única chamada ao modelo e permite que modelos locais menores processem projetos maiores de forma incremental.

---

## 📋 Pré-requisitos

Compatível com:

* Windows 11
* Linux
* macOS

É necessário ter instalado:

1. **Git**, disponível no `PATH`.
2. **Python 3.11 ou superior**.
3. **Ollama**.
4. Um modelo compatível instalado localmente.

Por padrão, o projeto utiliza o **Qwen3 4B**:

```bash
ollama pull qwen3:4b
```

Teste a instalação:

```bash
ollama run qwen3:4b
```

O Ollama é acessado por padrão em:

```text
http://127.0.0.1:11434
```

---

## 🚀 Instalação

Clone ou copie este projeto e abra um terminal dentro da pasta.

### Windows PowerShell

```powershell
py -3 -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

Copy-Item .env.example .env
```

Se o PowerShell bloquear a execução de scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

pip install -r requirements.txt

cp .env.example .env
```

---

## ▶️ Executando

Com o ambiente virtual ativado:

```bash
uvicorn app.main:app --reload
```

A aplicação estará disponível em:

```text
http://127.0.0.1:8000
```

A documentação interativa da API pode ser acessada em:

```text
http://127.0.0.1:8000/docs
```

---

## 🔍 Utilização

Informe uma URL pública do GitHub, por exemplo:

```text
https://github.com/usuario/repositorio
```

Após iniciar a análise, a interface acompanha o processamento em tempo real.

### Progresso da análise

O pipeline possui seis etapas principais:

```text
Ollama
   ↓
Clone
   ↓
Inventário
   ↓
Arquivos
   ↓
Síntese
   ↓
Concluído
```

Durante a execução são exibidos:

* etapa atual;
* progresso geral;
* quantidade de arquivos processados;
* quantidade de arquivos restantes;
* arquivos em processamento;
* tempo decorrido;
* tempo estimado restante (ETA);
* ritmo de processamento;
* chamadas ao modelo por minuto;
* linguagens detectadas.

### Pipeline completo

Internamente, a análise passa pelas seguintes etapas:

1. Validação e normalização da URL.
2. Verificação da disponibilidade do Ollama.
3. Clone local do repositório.
4. Inventário dos arquivos.
5. Detecção das linguagens utilizadas.
6. Análise estrutural de Python.
7. Extração de funções, classes e imports.
8. Leitura de documentação e arquivos de configuração.
9. Divisão de arquivos grandes em blocos.
10. Análise dos blocos pelo modelo local.
11. Consolidação da análise por arquivo.
12. Consolidação da análise do projeto.
13. Geração do relatório.
14. Cálculo da cobertura dos arquivos.

Arquivos que cabem em um único bloco são analisados diretamente, evitando uma chamada adicional de sumarização.

---

## 📄 Relatório

O relatório final é gerado em:

```text
workspace/reports/<id>/report.md
```

Cada execução também mantém seus dados intermediários em:

```text
workspace/runs/<id>/
```

O relatório busca apresentar, com base nas evidências encontradas no repositório:

* visão geral do projeto;
* stack tecnológica;
* linguagens;
* arquitetura;
* estrutura de diretórios;
* funcionalidades identificadas;
* componentes relevantes;
* dependências;
* evidências de implementação;
* possíveis problemas ou pontos de atenção;
* arquivos analisados;
* arquivos ignorados;
* cobertura da análise.

---

## 🧠 Como funciona a análise

O projeto **não envia o repositório inteiro para o modelo de uma única vez**.

Em vez disso, utiliza uma estratégia hierárquica:

```text
Repositório
    │
    ▼
Inventário
    │
    ▼
Arquivos
    │
    ▼
Blocos de código
    │
    ▼
Análise individual
    │
    ▼
Resumo por arquivo
    │
    ▼
Síntese do projeto
    │
    ▼
Relatório
```

Essa estratégia reduz a quantidade de contexto necessária em cada chamada e torna possível trabalhar com modelos locais menores.

### Cobertura

O sistema tenta analisar todos os arquivos de texto considerados elegíveis.

Entretanto, alguns arquivos podem ser excluídos por motivos como:

* formato binário;
* diretórios de dependências;
* diretórios de build;
* caches;
* arquivos acima do limite configurado;
* quantidade máxima de arquivos atingida.

Os arquivos excluídos são registrados no relatório para que a cobertura da análise seja identificável.

---

## ⚙️ Configuração

As configurações podem ser alteradas no arquivo `.env`:

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

### Principais parâmetros

| Variável                       | Função                                         |
| ------------------------------ | ---------------------------------------------- |
| `OLLAMA_BASE_URL`              | Endereço do servidor Ollama                    |
| `OLLAMA_MODEL`                 | Modelo utilizado na análise                    |
| `MAX_REPO_SIZE_MB`             | Tamanho máximo do repositório                  |
| `MAX_FILE_SIZE_KB`             | Tamanho máximo de um arquivo                   |
| `MAX_CHUNK_CHARS`              | Tamanho máximo dos blocos enviados ao modelo   |
| `MAX_FILES`                    | Número máximo de arquivos processados          |
| `WORKSPACE_DIR`                | Diretório de trabalho                          |
| `REQUEST_TIMEOUT_SECONDS`      | Timeout das requisições                        |
| `OLLAMA_KEEP_ALIVE`            | Tempo de permanência do modelo carregado       |
| `OLLAMA_THINK`                 | Configuração legada; thinking permanece sempre desativado |
| `OLLAMA_MAX_RETRIES`           | Número de novas tentativas após falhas         |
| `OLLAMA_RETRY_BACKOFF_SECONDS` | Intervalo entre tentativas                     |
| `MAX_SYNTHESIS_CHARS`          | Limite de contexto nas sínteses                |
| `OLLAMA_CONCURRENCY`           | Número de arquivos processados simultaneamente |

### Thinking desabilitado

O projeto força o thinking desativado para todos os modelos e não permite
reativá-lo por variável de ambiente. Cada requisição envia `think: false` e o
system prompt inclui `/nothink` quando necessário.

```env
OLLAMA_THINK=false
```

Essa variável é mantida apenas por compatibilidade. O cliente também descarta
o campo separado `message.thinking` da API e remove blocos `<think>...</think>`
e `<analysis>...</analysis>` que eventualmente apareçam em `message.content`,
inclusive blocos sem tag de fechamento ou com apenas a tag final `</think>`.

### Retry

As configurações:

```env
OLLAMA_MAX_RETRIES=2
OLLAMA_RETRY_BACKOFF_SECONDS=3
```

permitem repetir automaticamente chamadas que falharam por motivos transitórios, como timeout ou falha de comunicação com o Ollama.

Isso evita que uma falha pontual interrompa toda a análise.

### Orçamento de contexto

`MAX_SYNTHESIS_CHARS` limita a quantidade de conteúdo agregado enviada ao modelo durante as etapas de consolidação.

Isso é especialmente importante para modelos com janelas de contexto menores.

Quando o conteúdo excede o limite, a informação excedente é sinalizada no relatório.

### Concorrência

Por padrão:

```env
OLLAMA_CONCURRENCY=1
```

A análise ocorre sequencialmente.

É possível aumentar esse valor quando a infraestrutura do Ollama suportar múltiplas requisições simultâneas.

Em uma instalação local comum utilizando um único modelo, aumentar a concorrência pode simplesmente enfileirar as requisições e não necessariamente reduzir o tempo total.

---

## ⚡ Desempenho

O MVP possui algumas otimizações para reduzir o custo computacional e o número de chamadas ao modelo.

### Uma chamada para arquivos pequenos

Arquivos que cabem em um único bloco são enviados diretamente para análise consolidada.

Isso evita uma etapa intermediária de:

```text
código → resumo → análise do resumo
```

e utiliza:

```text
código → análise
```

### Conexão HTTP reutilizada

A comunicação com o Ollama utiliza uma conexão HTTP reaproveitada, reduzindo o overhead de estabelecer uma nova conexão a cada chamada.

### Clone raso

O repositório é clonado utilizando:

```text
--depth 1
--single-branch
--no-tags
```

Isso evita baixar histórico, branches adicionais e tags desnecessárias para a análise.

### Detecção de binários

A identificação de arquivos binários utiliza uma leitura inicial limitada, evitando carregar arquivos inteiros apenas para determinar seu tipo.

### Orçamento de contexto

A síntese utiliza `MAX_SYNTHESIS_CHARS` para evitar que grandes quantidades de informação sejam enviadas de uma só vez para modelos com contexto limitado.

### Concorrência opcional

`OLLAMA_CONCURRENCY` permite explorar paralelismo quando a infraestrutura disponível justificar seu uso.

---

## 🔌 API

### `POST /api/analyze`

Inicia uma nova análise.

Exemplo:

```json
{
  "url": "https://github.com/usuario/projeto"
}
```

Retorna o identificador da execução.

### `GET /api/runs`

Lista as execuções disponíveis na sessão atual do servidor.

Inclui informações como:

* ID;
* URL;
* status;
* etapa atual.

### `GET /api/runs/{run_id}`

Retorna o estado atual de uma execução.

### `GET /api/runs/{run_id}/report`

Retorna o relatório Markdown gerado para a execução.

---

## 🧪 Testes

Os testes automatizados cobrem componentes do scanner e funções auxiliares do pipeline, incluindo:

* detecção de linguagens;
* identificação de arquivos binários;
* inventário;
* validação de URLs;
* divisão em blocos;
* orçamento de contexto da síntese.

Instale as dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

Execute:

```bash
pytest
```

---

## ⚠️ Limitações atuais

Este projeto é um **MVP** e possui limitações importantes.

Atualmente não possui:

* banco de dados vetorial;
* embeddings;
* GraphRAG;
* análise AST aprofundada para todas as linguagens;
* execução dos testes do repositório analisado;
* análise dinâmica;
* autenticação com GitHub;
* suporte a repositórios privados;
* interface de perguntas e respostas sobre o repositório;
* grafo completo de dependências entre componentes.

A análise também depende da capacidade do modelo local utilizado. Modelos menores podem produzir análises menos precisas ou perder relações entre componentes de projetos grandes.

---

## 🎓 Objetivo acadêmico

Uma possível aplicação acadêmica do projeto é utilizar diversos repositórios de projetos técnicos como fonte para construir uma **base de conhecimento sobre desenvolvimento de software**.

A partir dessa base, seria possível investigar como técnicas de análise estática, recuperação de informação e IA generativa podem ser combinadas para permitir que sistemas de IA compreendam e consultem projetos de software de forma fundamentada em evidências extraídas diretamente do código e da documentação.

O MVP apresentado neste repositório representa a etapa de **ingestão, análise e estruturação das informações técnicas dos repositórios**.

---

