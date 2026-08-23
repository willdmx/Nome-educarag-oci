# 1. EducaRAG OCI

Agente inteligente de suporte educacional com RAG e Oracle Cloud Infrastructure.

O **EducaRAG OCI** é uma demonstração acadêmica de Retrieval-Augmented Generation (RAG) em Python. A aplicação recebe perguntas em português, consulta exclusivamente uma base de conhecimento fictícia em CSV e, quando configurada, usa um endpoint OpenAI-compatible do OCI Generative AI para redigir uma resposta fundamentada no contexto recuperado.

> **Aviso:** este projeto não representa políticas reais, não possui caráter oficial e não afirma parceria, patrocínio ou endosso da Oracle, da Alura ou de terceiros.

## 2. Badges

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Interface-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![RAG](https://img.shields.io/badge/RAG-TF--IDF%20%2B%20cosseno-5B5FC7)
![Projeto acadêmico](https://img.shields.io/badge/uso-projeto%20acad%C3%AAmico-6B7280)

Os badges descrevem apenas a tecnologia e a finalidade deste repositório; não indicam certificação ou vínculo institucional.

## 3. Descrição

A interface Streamlit permite que uma pessoa faça uma pergunta sobre a plataforma educacional fictícia EducaRAG. O mecanismo de recuperação transforma os registros do arquivo <code>data/base_conhecimento.csv</code> em documentos, cria um índice TF-IDF e seleciona os três registros com maior similaridade de cosseno em relação à pergunta.

O contexto recuperado pode seguir por dois caminhos:

- **OCI Generative AI:** o modelo recebe a pergunta e somente o contexto selecionado, com instruções para não inventar informações.
- **Modo de recuperação local:** quando a integração OCI não está configurada ou não está disponível, a aplicação apresenta a resposta recuperada diretamente do CSV, sem interromper o uso.

## 4. Problema

Plataformas educacionais concentram dúvidas recorrentes sobre acesso, matrículas, certificados, pagamentos e suporte. Procurar manualmente cada orientação aumenta o tempo de atendimento e pode produzir respostas inconsistentes.

Para uma prova de conceito acadêmica, também é importante demonstrar busca contextual sem depender de infraestrutura complexa, banco de dados vetorial ou disponibilidade permanente de um modelo generativo.

## 5. Solução

O EducaRAG OCI oferece uma solução pequena e auditável:

1. mantém o conhecimento em um CSV versionável;
2. utiliza recuperação lexical com TF-IDF e similaridade de cosseno;
3. limita o contexto aos três registros mais relevantes;
4. solicita ao modelo que responda apenas com base nesse contexto;
5. preserva a funcionalidade essencial por meio de fallback local;
6. expõe resposta, fontes e categorias na interface.

Essa abordagem reduz dependências operacionais e facilita a execução em uma VM Ubuntu.

## 6. Funcionalidades

- perguntas em português brasileiro por uma interface web simples;
- carregamento e validação da base de conhecimento CSV;
- combinação de categoria, pergunta e resposta em documentos pesquisáveis;
- normalização textual, vetorização TF-IDF e similaridade de cosseno;
- recuperação dos três registros mais relevantes;
- rejeição segura de perguntas sem similaridade mínima com a base;
- exibição das fontes consultadas e categorias encontradas;
- integração opcional com OCI Generative AI por endpoint OpenAI-compatible;
- prompt de sistema orientado a contexto, objetividade e não alucinação;
- fallback automático para recuperação local;
- perguntas de exemplo para demonstração;
- tratamento de arquivo inválido, pergunta vazia e falha no serviço externo.

## 7. Arquitetura

A aplicação possui três camadas principais:

| Camada | Responsabilidade |
|---|---|
| Interface (<code>app.py</code>) | Receber a pergunta, indicar o modo ativo e apresentar resposta, fontes e categorias. |
| Recuperação (<code>src/rag.py</code>) | Carregar o CSV, criar o índice TF-IDF, calcular similaridade e montar o contexto. |
| Geração (<code>src/llm.py</code>) | Chamar opcionalmente o endpoint OCI ou devolver uma resposta local segura. |

O CSV é a única fonte de conhecimento da demonstração. Não há banco de dados, LangChain, FAISS, ChromaDB, Docker, React ou Node.js.

## 8. Diagrama Mermaid

~~~mermaid
flowchart LR
    U[Usuário] --> S[Streamlit]
    S --> R[Retriever<br/>TF-IDF + similaridade de cosseno]
    R --> B[(CSV<br/>data/base_conhecimento.csv)]
    B --> C[Contexto<br/>3 registros mais relevantes]
    C --> D{OCI GenAI<br/>configurado?}
    D -- Sim --> O[OCI Generative AI<br/>endpoint OpenAI-compatible]
    O --> A[Resposta]
    D -- Não ou indisponível --> F[Fallback local<br/>resposta recuperada do CSV]
    F --> A
~~~

O diagrama representa o fluxo conceitual da consulta. Na inicialização, o retriever carrega e indexa o CSV; a cada pergunta, ele consulta esse índice para construir o contexto.

## 9. Fluxo RAG

1. **Carregamento:** o arquivo CSV é lido em UTF-8 e suas colunas obrigatórias são verificadas.
2. **Documentos:** <code>categoria</code>, <code>pergunta</code> e <code>resposta</code> são combinadas para cada registro.
3. **Indexação:** o <code>TfidfVectorizer</code> converte os documentos em uma matriz esparsa.
4. **Consulta:** a pergunta do usuário é transformada com o mesmo vocabulário.
5. **Ranking:** a similaridade de cosseno compara a consulta com todos os documentos.
6. **Recuperação:** os três registros mais relevantes são selecionados.
7. **Validação de relevância:** se o melhor resultado tiver similaridade menor que 0,20, nenhum contexto é liberado para resposta e o sistema informa que a base não contém informação suficiente.
8. **Contexto:** pergunta, resposta, categoria e fonte dos registros recuperados são organizadas para uso posterior.
9. **Resposta:** o contexto é enviado ao OCI Generative AI quando configurado; caso contrário, a melhor resposta do CSV é exibida diretamente.

TF-IDF privilegia termos importantes dentro da coleção. Por ser uma busca lexical, palavras equivalentes escritas de formas muito diferentes podem obter pontuações menores.

## 10. Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.10 ou superior | Linguagem e ambiente de execução. |
| Streamlit | Interface web. |
| pandas | Leitura e validação do CSV. |
| scikit-learn | TF-IDF e similaridade de cosseno. |
| OpenAI Python SDK 1.x | Cliente para endpoint OpenAI-compatible. |
| python-dotenv | Carregamento opcional do arquivo <code>.env</code>. |
| OCI Generative AI | Geração opcional de resposta contextual. |

As faixas de versão em <code>requirements.txt</code> limitam mudanças de versão principal. A combinação resolvida durante esta validação foi testada em Python 3.12; em implantação, execute <code>pip check</code> depois da instalação.

## 11. Estrutura do repositório

~~~text
educarag-oci/
├── app.py
├── data/
│   └── base_conhecimento.csv
├── docs/
│   └── evidencias/
│       └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── llm.py
│   └── rag.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
~~~

## 12. Base de conhecimento

O arquivo <code>data/base_conhecimento.csv</code> contém conteúdo inteiramente fictício, criado para demonstração acadêmica. Ele usa as colunas:

| Coluna | Finalidade |
|---|---|
| <code>categoria</code> | Agrupa o assunto, como certificado, senha ou pagamento. |
| <code>pergunta</code> | Registra uma dúvida representativa. |
| <code>resposta</code> | Contém a orientação fictícia que fundamentará a resposta. |
| <code>fonte</code> | Identifica a referência interna fictícia exibida na interface. |

A base possui pelo menos 25 registros e cobre matrículas, acesso aos cursos, senha, certificados, conclusão, avaliações, reembolsos, cancelamentos, suporte, bolsas, pagamentos, documentos, prazos, privacidade e proteção de dados.

Para ampliar a base, adicione linhas preservando o cabeçalho, a codificação UTF-8 e campos textuais completos. Não inclua dados pessoais, credenciais, políticas reais ou material confidencial.

## 13. Como instalar

### Pré-requisitos

- Python 3.10 ou superior;
- <code>pip</code>;
- Git, caso o projeto seja clonado de um repositório.

### Linux ou macOS

~~~bash
git clone https://github.com/SEU_USUARIO/educarag-oci.git
cd educarag-oci
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

### Windows PowerShell

~~~powershell
git clone https://github.com/SEU_USUARIO/educarag-oci.git
Set-Location educarag-oci
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

Substitua <code>SEU_USUARIO</code> pelo proprietário real do repositório quando ele for publicado.

## 14. Como executar localmente

Com o ambiente virtual ativado e na raiz do projeto:

~~~bash
streamlit run app.py
~~~

O Streamlit normalmente informa no terminal o endereço local de acesso, como <code>http://localhost:8501</code>. Para encerrar, pressione <code>Ctrl+C</code>.

O arquivo <code>.env</code> não é obrigatório. Sem as quatro variáveis OCI preenchidas, a interface deve indicar **Modo de recuperação local** e continuar respondendo a partir do CSV.

## 15. Configuração das variáveis OCI

Crie o arquivo local de configuração a partir do modelo:

~~~bash
cp .env.example .env
~~~

No Windows PowerShell:

~~~powershell
Copy-Item .env.example .env
~~~

Preencha apenas no seu ambiente:

~~~dotenv
OCI_GENAI_BASE_URL=
OCI_GENAI_API_KEY=
OCI_GENAI_PROJECT_ID=
OCI_GENAI_MODEL=
~~~

| Variável | Descrição |
|---|---|
| <code>OCI_GENAI_BASE_URL</code> | URL base OpenAI-compatible apresentada pela configuração do seu serviço OCI. |
| <code>OCI_GENAI_API_KEY</code> | Chave utilizada pelo endpoint; deve permanecer secreta. |
| <code>OCI_GENAI_PROJECT_ID</code> | Identificador do projeto requerido pela configuração escolhida. |
| <code>OCI_GENAI_MODEL</code> | Identificador exato de um modelo compatível com a API Chat Completions no projeto e na região escolhidos. |

Não copie valores de exemplo de outro ambiente. Use os dados exibidos para o seu próprio projeto e região. O arquivo <code>.env</code> está ignorado pelo Git.

## 16. Integração com OCI Generative AI

O módulo <code>src/llm.py</code> usa o SDK Python da OpenAI como cliente de um endpoint compatível. A integração é opcional e foi isolada da camada de recuperação.

Antes de configurar o modo generativo, crie um projeto do OCI Generative AI, gere uma API key na mesma região do modelo, conceda as permissões necessárias e selecione um modelo/região que suporte <code>/chat/completions</code>. Consulte a documentação oficial sobre [uso de projetos](https://docs.oracle.com/en-us/iaas/Content/generative-ai/use-project.htm) e a [API Chat Completions da OCI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-completions-api.htm).

Com todas as variáveis válidas, o fluxo esperado é:

1. criar o cliente com a URL base e a chave do ambiente;
2. selecionar o modelo configurado;
3. enviar um prompt de sistema que exige uso exclusivo do contexto;
4. enviar pergunta e contexto recuperado;
5. retornar uma resposta objetiva em português brasileiro.

Se faltar configuração, a chamada generativa é ignorada. Se o endpoint falhar, a aplicação usa a recuperação local e informa o modo ao usuário, sem expor segredos.

Endpoints, cabeçalhos e identificadores podem variar conforme a configuração disponibilizada na OCI. Compare <code>src/llm.py</code> com o trecho **How to use** exibido no seu projeto OCI Generative AI e adapte somente os parâmetros necessários. Esta documentação é genérica e não substitui a documentação aplicável à sua conta.

## 17. Deploy em VM Ubuntu na OCI

As etapas abaixo são genéricas para uma VM Ubuntu com acesso por SSH. Os nomes, endereços e regras de rede dependem do ambiente do responsável pelo deploy.

### 17.1 Preparar a VM

~~~bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
git clone https://github.com/SEU_USUARIO/educarag-oci.git
cd educarag-oci
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

### 17.2 Configurar o ambiente

~~~bash
cp .env.example .env
nano .env
~~~

Preencha os valores apenas se utilizar OCI Generative AI. Proteja o arquivo para que somente o usuário da aplicação possa lê-lo:

~~~bash
chmod 600 .env
~~~

Também é válido manter todas as variáveis vazias para executar no modo local.

### 17.3 Iniciar a aplicação

~~~bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
~~~

O processo permanece associado à sessão do terminal. Para uma publicação persistente, configure posteriormente um gerenciador de serviços, como <code>systemd</code>, com usuário sem privilégios e diretório de trabalho explícito.

### 17.4 Rede e acesso

- permita a porta TCP 8501 no firewall e na regra de entrada da rede OCI somente para os endereços que realmente precisem acessar a demonstração;
- para exposição pública, prefira um proxy reverso com HTTPS e não exponha arquivos do projeto;
- valide o acesso por <code>http://IP_DA_VM:8501</code> apenas depois de aplicar as regras de rede;
- não coloque chaves em comandos, imagens, histórico do shell, repositório ou capturas de tela.

Este projeto não usa Docker e não provisiona recursos OCI automaticamente.

## 18. Perguntas de exemplo

Use estas perguntas para validar os principais temas:

1. Como faço para obter meu certificado?
2. Qual é o prazo para solicitar reembolso?
3. Como redefinir minha senha?
4. Como funciona o programa de bolsas?
5. Como cancelar uma matrícula?

Variações em linguagem natural também podem funcionar, mas a recuperação lexical tende a responder melhor quando a pergunta contém termos presentes no CSV.

## 19. Respostas esperadas

Os textos exatos podem variar no modo generativo. O conteúdo, porém, deve permanecer fiel aos registros recuperados:

| Pergunta | Comportamento esperado |
|---|---|
| Certificado | Exigir conclusão dos módulos obrigatórios e nota mínima; orientar <code>Painel > Certificado > Emitir certificado</code>, com PDF imediato. |
| Reembolso | Informar prazo de até 7 dias corridos após a compra e o critério de menos de 20% do conteúdo acessado. |
| Redefinição de senha | Orientar <code>Esqueci minha senha</code>, uso do link por e-mail e expiração em 30 minutos. |
| Bolsas | Informar bolsas integrais ou de 50%, seleção socioeducacional, carta de motivação e edital de cada ciclo. |
| Cancelamento de matrícula | Orientar <code>Minhas matrículas > Solicitar cancelamento</code> e processamento em até 1 dia útil. |

No modo local, espera-se uma resposta diretamente baseada no registro mais relevante. No modo OCI, a redação pode ser sintetizada a partir dos três resultados. Se o contexto não sustentar uma resposta, o modelo deve informar que não encontrou informação suficiente na base de conhecimento.

## 20. Evidências

O diretório <code>docs/evidencias/</code> foi reservado para materiais de validação. Sugestões:

- tela inicial com o indicador do modo ativo;
- execução das cinco perguntas de exemplo;
- resposta com fontes e categorias;
- funcionamento sem variáveis OCI;
- funcionamento com OCI, quando houver ambiente autorizado;
- terminal com instalação e inicialização concluídas.

Use nomes descritivos, por exemplo <code>01-modo-local.png</code> e <code>02-certificado.png</code>. Antes de publicar uma evidência, remova chaves, identificadores sensíveis, endereços privados, nomes pessoais e demais dados que não devam ser públicos. O arquivo <code>.gitkeep</code> apenas mantém a pasta vazia sob controle de versão.

## 21. Limitações

- TF-IDF mede correspondência lexical e não compreende plenamente sinônimos ou intenção.
- O limiar de similaridade de 0,20 é uma heurística calibrada para esta base pequena; novas entradas exigem nova avaliação.
- A base é pequena, estática e inteiramente fictícia.
- Apenas os três resultados mais relevantes compõem o contexto.
- Não há memória de conversa, autenticação, autorização ou painel administrativo.
- Não existe banco de dados nem mecanismo de atualização online do conteúdo.
- A disponibilidade e a latência do modo generativo dependem do endpoint configurado.
- Respostas geradas podem variar; fontes e contexto recuperado devem ser usados para conferência.
- A aplicação é uma demonstração, não um canal real de atendimento.

## 22. Melhorias futuras

- criar testes automatizados para carregamento, ranking e fallback;
- medir precisão com um conjunto fixo de perguntas e respostas esperadas;
- adicionar busca semântica mantendo uma opção leve de execução;
- destacar pontuações de similaridade na área de evidências;
- validar alterações no CSV em integração contínua;
- melhorar acessibilidade, observabilidade e mensagens de erro;
- adicionar cache controlado para bases maiores;
- servir a aplicação atrás de proxy HTTPS;
- documentar uma política de atualização e revisão do conteúdo fictício.

## 23. Segurança

- nunca grave credenciais no código, no CSV ou no README;
- mantenha <code>.env</code> fora do Git e restrinja suas permissões;
- revogue imediatamente qualquer segredo exposto;
- use credenciais com menor privilégio e prazo de vida adequados ao ambiente;
- não registre prompts, respostas ou identificadores se puderem conter dados sensíveis;
- limite portas e origens nas regras de rede da VM;
- use HTTPS para tráfego fora de uma rede controlada;
- mantenha Python e dependências atualizados após validação;
- trate todo conteúdo exibido como não confiável e evite inserir dados pessoais na demonstração;
- considere um serviço de segredos apropriado em ambientes além da prova de conceito.

O fallback local não elimina a necessidade de proteger o host e a base de conhecimento.

## 24. Licença e projeto acadêmico

Projeto acadêmico desenvolvido para o **Challenge Alura Agente - Oracle Next Education.**

Todo o conteúdo da plataforma EducaRAG e de sua base de conhecimento é fictício e foi criado exclusivamente para demonstração. O repositório não é um produto oficial e não implica parceria, suporte ou endosso da Alura, da Oracle ou de qualquer terceiro.

Nenhuma licença de reutilização foi definida neste escopo. Antes da publicação, o responsável pelo repositório deve adicionar um arquivo <code>LICENSE</code> caso deseje conceder permissões explícitas de uso, cópia ou modificação.
