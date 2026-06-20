# 🎓 Assistente Acadêmico IA — Sistema Multiagente com LLMs

> Sistema multiagente baseado em LLaMA local para apoio aos estudos: responde perguntas sobre matérias, cria cronogramas de estudo e busca contexto em documentos acadêmicos.

---

## 👥 Integrantes da Equipe

Gabriel Castanho da Rosa | 199046

---

## 📋 Descrição do Problema

Estudantes universitários frequentemente têm dificuldade em:
1. Revisar conteúdos de múltiplas disciplinas de forma eficiente.
2. Organizar cronogramas de estudo realistas antes de provas.
3. Encontrar explicações claras nos materiais do curso (PDFs, slides, notas).

O problema se beneficia de uma arquitetura multiagente porque diferentes tipos de demanda exigem estratégias distintas: uma pergunta conceitual requer busca semântica em documentos; um pedido de cronograma requer raciocínio sobre datas e distribuição de tópicos; ambos requerem síntese linguística fluente. Delegar cada responsabilidade a um agente especializado torna o sistema mais preciso e manutenível do que um agente único tentando fazer tudo.

---

## 🎯 Objetivo da Solução

Construir um assistente de terminal baseado em LLaMA local que:
- Responda perguntas acadêmicas com base em documentos indexados (RAG).
- Gere cronogramas de estudos personalizados a partir de tópicos e datas informadas.
- Forneça dicas de aprendizado e gestão do tempo.
- Opere 100% offline, sem dependência de APIs pagas.

---
