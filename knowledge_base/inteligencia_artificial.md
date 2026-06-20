# Inteligência Artificial — Resumo dos Conceitos Fundamentais

## 1. O que é Inteligência Artificial?

Inteligência Artificial (IA) é o campo da ciência da computação dedicado ao desenvolvimento de sistemas capazes de realizar tarefas que, normalmente, requerem inteligência humana: raciocínio, aprendizado, percepção, tomada de decisão e comunicação em linguagem natural.

---

## 2. Tipos de IA

### IA Estreita (Narrow AI)
Projetada para uma tarefa específica. É o tipo predominante hoje.
Exemplos: reconhecimento facial, tradutores automáticos, chatbots, sistemas de recomendação.

### IA Geral (AGI)
Capaz de realizar qualquer tarefa cognitiva que um humano possa fazer. Ainda teórica.

### IA Super-humana (Superinteligência)
Hipotética; superaria o ser humano em todas as capacidades intelectuais.

---

## 3. Machine Learning (Aprendizado de Máquina)

Subcampo da IA em que os sistemas aprendem a partir de dados sem serem explicitamente programados.

### Aprendizado Supervisionado
O modelo aprende com dados rotulados (entrada → saída esperada).
- Exemplos: classificação de e-mails como spam, previsão de preços.
- Algoritmos: Regressão Linear, SVM, Redes Neurais, Random Forest.

### Aprendizado Não Supervisionado
O modelo descobre padrões em dados sem rótulos.
- Exemplos: segmentação de clientes, detecção de anomalias.
- Algoritmos: K-Means, DBSCAN, PCA, Autoencoders.

### Aprendizado por Reforço
O agente aprende interagindo com o ambiente e recebendo recompensas ou punições.
- Exemplos: jogos (AlphaGo), robótica, navegação autônoma.

---

## 4. Redes Neurais Artificiais

Inspiradas no cérebro humano, compostas por neurônios artificiais organizados em camadas:
- **Camada de entrada**: recebe os dados brutos.
- **Camadas ocultas**: extraem representações progressivamente mais abstratas.
- **Camada de saída**: produz o resultado final.

### Perceptron
Neurônio artificial básico: calcula uma soma ponderada das entradas e aplica uma função de ativação.

### Funções de Ativação:
- **ReLU** (f(x) = max(0,x)): mais comum nas camadas ocultas.
- **Sigmoid**: converte saída para [0,1], usada em classificação binária.
- **Softmax**: converte saída para distribuição de probabilidades (multiclasse).

### Backpropagation
Algoritmo que calcula os gradientes do erro em relação a cada peso e os propaga de volta pela rede, atualizando os pesos via gradiente descendente.

---

## 5. Deep Learning

Redes neurais com muitas camadas ocultas capazes de aprender representações hierárquicas.

### CNN (Redes Convolucionais)
Especializadas em dados com estrutura espacial, como imagens.
Usam filtros convolucionais para extrair bordas, texturas e padrões.

### RNN (Redes Recorrentes)
Processam sequências (texto, séries temporais). Mantêm estado interno (memória).

### LSTM (Long Short-Term Memory)
Variação da RNN que resolve o problema do gradiente desaparecente.
Usa portões (input, forget, output) para controlar o fluxo de informação.

### Transformers
Arquitetura baseada em mecanismo de atenção (Self-Attention).
Base dos modelos de linguagem modernos como GPT, BERT, LLaMA.
Processam sequências inteiras em paralelo (ao contrário das RNNs).

---

## 6. LLMs — Modelos de Linguagem de Grande Escala

LLMs são redes neurais gigantescas treinadas em enormes corpora de texto.
Capazes de gerar texto, responder perguntas, traduzir, codificar e raciocinar.

### Exemplos:
- GPT-4 (OpenAI), Claude (Anthropic), LLaMA (Meta), Gemini (Google).

### Como funcionam:
Treinados para prever o próximo token (pedaço de texto) com base no contexto anterior.
Durante inferência, geram texto token por token de forma autoregressiva.

### Fine-tuning e RLHF:
- **Fine-tuning**: ajuste do modelo com dados específicos de uma tarefa.
- **RLHF** (Reinforcement Learning from Human Feedback): alinha o comportamento do modelo com preferências humanas.

---

## 7. RAG — Retrieval-Augmented Generation

Técnica que combina busca de informação com geração de texto:
1. A pergunta do usuário é transformada em embedding.
2. O embedding é comparado com uma base vetorial de documentos.
3. Os trechos mais relevantes são recuperados e inseridos no prompt.
4. O LLM gera a resposta com base no contexto recuperado.

### Vantagens:
- Reduz alucinações do modelo.
- Permite usar documentos atualizados sem re-treinar.
- Fornece referências às fontes.

---

## 8. Agentes de IA

Um agente de IA é um sistema que percebe o ambiente, raciocina e toma ações para atingir objetivos.

### Componentes:
- **Percepção**: entrada de dados do ambiente.
- **Memória**: histórico de contexto e informações relevantes.
- **Raciocínio**: uso de LLM para decidir a próxima ação.
- **Ação**: chamada de ferramentas, APIs ou outros agentes.

### Arquiteturas Multiagente:
- Múltiplos agentes especializados cooperam.
- Cada agente tem um papel definido (planejador, executor, revisor...).
- A comunicação entre agentes pode seguir protocolos como MCP.

---

## 9. Embeddings

Representação vetorial densa de texto, imagens ou outros dados.
Itens semanticamente similares têm vetores próximos no espaço vetorial.

### Usos:
- Busca semântica (RAG).
- Agrupamento de documentos.
- Classificação de intenção.
- Detecção de similaridade.

### Exemplos de modelos de embeddings:
- text-embedding-ada-002 (OpenAI), nomic-embed-text, all-MiniLM-L6-v2.

---

## 10. Ética em IA

Temas fundamentais para o desenvolvimento responsável de sistemas de IA:
- **Viés algorítmico**: modelos treinados em dados tendenciosos podem perpetuar discriminação.
- **Explicabilidade**: a necessidade de entender como o modelo chegou a uma decisão.
- **Privacidade**: uso responsável de dados pessoais no treinamento.
- **Impacto no emprego**: automação de tarefas cognitivas e mercado de trabalho.
- **Alinhamento**: garantir que sistemas de IA ajam de acordo com valores humanos.
