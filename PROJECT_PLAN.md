# FleetGuard AI — Predictive Maintenance & Fleet Intelligence Platform

> Plano de execução incremental para um portfólio de Dados que evolui para Arquitetura de Soluções em IA.

## 1. Contexto, propósito e limites

FleetGuard AI é uma plataforma fictícia de inteligência de frota para motocicletas urbanas. Ela usa telemetria e histórico de manutenção para priorizar inspeções, estimar risco de manutenção e, posteriormente, acompanhar saúde de baterias de motos elétricas.

**Objetivo profissional de curto prazo:** entregar uma versão demonstrável para vagas de Dados, com análise, SQL, modelagem, dashboard e uma API simples.  
**Objetivo de evolução:** demonstrar decisões de integração, dados, ML, segurança, operação e escalabilidade relevantes a uma trajetória de AI Solutions Architect.

O projeto é inspirado em desafios públicos e genéricos de mobilidade, telemetria e manutenção de frotas. **Não reproduz, infere nem alega representar sistemas internos, dados, limites técnicos ou arquitetura de Mottu, Vammo ou qualquer outra empresa.** Todos os dados, limiares e cenários iniciais são simulados e devem ser identificados como tal no README e dashboards.

### Problema de negócio

Uma operação não deve tratar todas as motos da mesma forma. O FleetGuard transforma sinais de uso e manutenção em uma fila priorizada: quais veículos devem ser inspecionados primeiro, quais fatores explicam o risco e qual é o panorama de saúde da frota.

### Perguntas que a primeira versão responde

- Quais veículos apresentam maior risco de manutenção preventiva?
- Quais sinais contribuíram para esse risco?
- Como variam quilometragem, temperatura, vibração e eventos de condução?
- Quais bases, modelos e tipos de veículo exigem mais atenção?
- Para elétricas: quais baterias têm comportamento anômalo no conjunto simulado?

### Fora de escopo inicial

- Diagnóstico mecânico certificado ou recomendação de segurança real.
- Controle de veículos, cobrança, rastreamento individual em produção ou decisões automáticas.
- Streaming, Kubernetes, data warehouse gerenciado, Kafka, SageMaker ou microserviços múltiplos antes de a versão mínima estar validada.

## 2. Princípios arquiteturais

1. **Evolução, não complexidade teatral:** comece com arquivo local e um único serviço Python.
2. **Dados primeiro:** modelo de ML só entra depois de qualidade, entendimento estatístico e baseline de regras.
3. **Separar camadas:** bruto, processado, dados relacionais, artefatos de modelo e relatórios nunca se confundem.
4. **Rastreabilidade:** toda predição informa versão de modelo, data, entrada e explicação simples.
5. **Privacidade por padrão:** IDs sintéticos; nenhuma PII, placa, documento ou localização precisa no dataset público.
6. **Falhar com clareza:** eventos inválidos são rejeitados/quarentenados; não são silenciosamente “consertados”.
7. **Uma decisão por ADR:** decisões relevantes têm contexto, alternativas, escolha e consequência.
8. **Cloud pragmática:** a Magalu Cloud é o provedor atual do projeto por causa dos créditos do hackathon; serviços devem ser adicionados somente quando agregarem valor demonstrável.
9. **Portabilidade:** o uso de Object Storage compatível com S3 deve manter o código desacoplado do provedor sempre que possível.
10. **Enterprise como evolução:** SAP HANA e SAP Fiori entram depois do MVP e somente quando a integração tiver um caso de uso claro.

## 3. Arquitetura evolutiva

```text
FASES 0–6 (local)
CSV simulado -> Python/Pandas -> Parquet/CSV processado -> PostgreSQL
                                              |                |
                                           Excel/Power BI    SQL/KPIs

FASES 7–8 (produto demonstrável)
PostgreSQL + modelo Joblib -> FastAPI -> dashboard/cliente
                 ^                 |
          treinamento Python       +-> predições auditáveis

FASES 9–15 (Magalu Cloud e arquitetura)
Magalu Object Storage (S3-compatible) <-> VM + Docker Compose
                                              |       |
                                         FastAPI  Clojure event gateway
                                              |
                                      PostgreSQL DBaaS
                                              |
                                   logs, métricas, segurança
                                              |
                                  ┌───────────┴───────────┐
                                  │                       │
                              SAP HANA               SAP Fiori
                           analytics/integração    interface enterprise
```

**Componentes e responsabilidades**

| Componente | Responsabilidade | Não deve fazer |
|---|---|---|
| Gerador | Produzir telemetria sintética reproduzível | Fingir dados reais |
| ETL Python | Validar, limpar e criar features | Servir HTTP |
| PostgreSQL | Fonte relacional para operação/BI | Armazenar arquivo de modelo |
| Treinamento | Avaliar e versionar modelo | Alterar dados brutos |
| FastAPI | Consultar saúde e executar inferência | Retreinar em requisição |
| Clojure (tardio) | Validar/normalizar eventos de entrada | Duplicar regras analíticas |
| Magalu Object Storage (tardio) | Data lake e artefatos; compatibilidade com fluxo S3 | Banco transacional |
| PostgreSQL DBaaS (tardio) | Banco relacional gerenciado | Armazenar modelos ML |
| SAP HANA (evolução) | Analytics e integração corporativa | Substituir o banco operacional sem justificativa |
| SAP Fiori (evolução) | Interface corporativa orientada a papéis | Executar ETL ou ML |

## 4. Estrutura de diretórios proposta

```text
fleetguard-ai/
├── PROJECT_PLAN.md
├── README.md
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── data/                       # ignorado pelo Git, salvo exemplos mínimos
│   ├── raw/
│   ├── processed/
│   └── exports/
├── docs/
│   ├── adr/
│   ├── data_dictionary.md
│   ├── architecture.md
│   ├── runbooks/
│   └── phase_reports/
├── notebooks/                  # exploração; lógica produtiva vai para src/
├── sql/
│   ├── ddl/
│   ├── queries/
│   └── seeds/
├── src/fleetguard/
│   ├── simulation/
│   ├── ingestion/
│   ├── transformation/
│   ├── analytics/
│   ├── ml/
│   ├── api/
│   └── common/
├── services/event-gateway/     # Clojure, somente na Fase 12
├── tests/
├── artifacts/                  # modelos/relatórios locais; ignorado no Git
└── infra/
    ├── docker/
    └── aws/
```

## 5. Domínio e contrato de dados

### Entidades principais

```text
vehicle 1---N telemetry_reading
vehicle 1---N maintenance_event
vehicle 1---N prediction
battery 1---N battery_reading     (somente elétricas)
vehicle 0..1---1 battery
```

### Dataset de telemetria (simulado)

| Campo | Tipo | Aplicação | Regra |
|---|---|---|---|
| `vehicle_id` | string | todos | ID sintético estável |
| `timestamp` | UTC timestamp | todos | não nulo; por veículo, crescente |
| `vehicle_type` | enum | todos | `combustion` ou `electric` |
| `base_id` | string | todos | base operacional sintética |
| `odometer_km` | decimal | todos | >= 0 e não decrescente por veículo |
| `speed_kmh` | decimal | todos | >= 0 |
| `acceleration_mps2` | decimal | todos | faixa plausível simulada |
| `hard_braking_events` | integer | todos | >= 0 |
| `hard_acceleration_events` | integer | todos | >= 0 |
| `trip_duration_min` | decimal | todos | >= 0 |
| `engine_temperature_c` | decimal/null | combustão | nulo para elétrica |
| `rpm` | integer/null | combustão | nulo para elétrica |
| `oil_service_km` | decimal/null | combustão | km desde serviço |
| `motor_temperature_c` | decimal/null | elétrica | nulo quando indisponível |
| `battery_id` | string/null | elétrica | obrigatório para elétrica |
| `battery_soc_pct` | decimal/null | elétrica | 0–100 |
| `battery_temperature_c` | decimal/null | elétrica | valor simulado |
| `battery_voltage_v` | decimal/null | elétrica | valor simulado |
| `charging_cycles` | integer/null | elétrica | >= 0 |
| `maintenance_label_30d` | 0/1 | treinamento | rótulo sintético futuro; nunca feature |

`maintenance_label_30d = 1` significa que, no cenário sintético, há evento de manutenção nos 30 dias seguintes à leitura. Não significa falha física confirmada.

### Regras contra leakage

- Jamais usar `maintenance_label_30d`, data futura de manutenção, status posterior ou qualquer coluna derivada do futuro como feature.
- Dividir treino/teste por tempo; não embaralhar leituras temporais aleatoriamente.
- Calcular janelas móveis apenas com observações até o instante da linha.
- Fazer ajuste de imputação, escala e seleção de features dentro do pipeline de treino.

## 6. Geração de dados simulados

O gerador recebe `seed`, período, quantidade de veículos, proporção elétrica e taxa-alvo aproximada de manutenção. Deve produzir cenários normal, atenção e elevado risco com tendência gradual, ruído e dados ausentes controlados.

Exemplo de contrato de execução:

```bash
python -m fleetguard.simulation.generate \
  --seed 42 --vehicles 200 --days 90 --electric-ratio 0.35 \
  --output data/raw/telemetry_2026_q1.csv
```

Pseudocódigo vetorizado:

```python
risk_signal = (0.35 * km_since_service_norm + 0.25 * temp_deviation_norm
               + 0.20 * vibration_proxy_norm + 0.20 * harsh_events_norm)
maintenance_probability = sigmoid(risk_signal + noise)
```

Os pesos são apenas mecanismos de simulação. Documente seed, distribuição, proporção de nulos, anomalias inseridas e limitações no relatório da fase. Não apresente limiares como especificações técnicas reais.

## 7. Processo obrigatório em toda fase

```text
Planejar -> Grill-me -> Implementar -> Testar -> Code Review
       -> Corrigir -> Documentar -> Avaliar gate -> Avançar
```

### Regras rígidas para OpenCode/agente

1. Trabalhe em **uma única fase ativa**. Leia este plano e o relatório da fase anterior antes de editar.
2. Antes de código, entregue um plano de até uma página: objetivo, arquivos, riscos, testes e ADR necessário.
3. Execute o Grill-me antes da implementação; registre respostas e lacunas em `docs/phase_reports/phase-XX.md`.
4. Não criar infraestrutura, serviço, dependência ou diretório de uma fase futura sem aprovação explícita do usuário.
5. Não marcar item concluído sem evidência reproduzível: comando, saída resumida, teste, screenshot ou consulta SQL.
6. Não usar “accuracy alta” como aprovação exclusiva do ML. Reportar precisão, recall, F1, PR-AUC e matriz de confusão quando aplicável.
7. Não modificar schema, contrato de API ou regra de dados sem teste e ADR quando a mudança for duradoura.
8. Não expor segredos; usar `.env.example`, variáveis de ambiente e valores fictícios.
9. Ao falhar um gate, corrija somente a fase atual. Não contorne o problema avançando de fase.
10. Ao fim, pare e solicite aprovação humana para iniciar a próxima fase.

### Definition of Done (DoD) universal

Uma fase só está pronta quando todos os itens aplicáveis forem verdadeiros:

- [ ] Objetivo e escopo documentados; fora de escopo explícito.
- [ ] Critérios de aceitação atendidos e evidenciados.
- [ ] Código legível, formatado e sem credenciais.
- [ ] Testes relevantes verdes; caso de borda e erro cobertos.
- [ ] Revisão de código feita contra esta DoD.
- [ ] Documentação, comando de execução e rollback/limitação atualizados.
- [ ] Perguntas Grill-me respondidas ou lacunas registradas.
- [ ] ADR criado/atualizado se houve decisão arquitetural.
- [ ] Usuário aprovou o avanço.

## 8. Fases incrementais

### Fase 0 — Fundação e contrato

**Objetivo:** criar repositório, convenções, dicionário de dados e gerador mínimo reproduzível.

**Entregas:** `README` inicial, `pyproject.toml`, lint/format, `.gitignore`, `.env.example`, `docs/data_dictionary.md`, gerador de 20 veículos/7 dias e teste de schema.

**Grill-me:** Por que UTC? Por que IDs sintéticos? Quais campos são nulos por tipo de veículo? Como reproduzir exatamente o dataset?

**Gate:** CSV é gerado duas vezes com mesma seed e conteúdo determinístico; validação rejeita SOC fora de 0–100 e odômetro negativo.

### Fase 1 — Python, Pandas, NumPy e EDA

**Objetivo:** transformar telemetria bruta em uma análise confiável, sem banco, API ou ML.

**Implementar:** carga tipada; tratamento justificado de nulos/duplicatas; `merge`, `concat`, `groupby`, `pivot_table`, `melt`; `rolling` por veículo; NumPy vetorizado; gráficos Matplotlib/Seaborn; relatório EDA.

**Métricas:** registros, veículos, período, nulos, duplicatas, distribuição, quartis, média, mediana, desvio padrão e outliers por tipo.

**Gate:** pipeline gera `data/processed/telemetry_features.parquet`; janelas não misturam veículos; mínimo seis gráficos com interpretação; testes cobrem timestamp, duplicata e cálculo de janela.

### Fase 2 — PostgreSQL e modelagem de dados

**Objetivo:** persistir a operação em modelo relacional simples e íntegro.

**Implementar:** DDL versionado para `vehicles`, `telemetry_readings`, `maintenance_events`, `batteries`, `battery_readings`, `predictions`; PK/FK, checks, `UNIQUE(vehicle_id, timestamp)`, índices para consulta temporal; carga idempotente.

**ADR-001:** PostgreSQL como store relacional operacional/analítico inicial, em vez de banco especializado de séries temporais.

**Gate:** banco sobe localmente; carga repetida não duplica leituras; plano de consulta demonstra uso do índice em histórico por veículo; diagrama ER atualizado.

### Fase 3 — SQL avançado e KPIs

**Objetivo:** produzir inteligência diretamente no banco.

**Implementar:** CTEs, janelas (`LAG`, `AVG OVER`, `ROW_NUMBER`), percentis, agregações e views para: top risco por base, tendência de telemetria, km desde manutenção e saúde da frota.

Exemplo:

```sql
SELECT vehicle_id, timestamp,
       AVG(speed_kmh) OVER (
         PARTITION BY vehicle_id ORDER BY timestamp
         ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
       ) AS speed_mean_24_readings
FROM telemetry_readings;
```

**Gate:** ao menos cinco consultas versionadas, cada uma com pergunta de negócio, explicação e teste de resultado; consulta de ranking possui critério determinístico de desempate.

### Fase 4 — Estatística aplicada e baseline de risco

**Objetivo:** criar interpretação estatística antes de ML.

**Implementar:** distribuição/frequência, variância, desvio padrão, quartis, IQR, percentis, limites de tolerância **simulados**, comparação por tipo de veículo e um score de regras explicável.

Exemplo de saída: `HIGH` se score >= 0.75; pesos e corte são parâmetros simulados versionados, não regras mecânicas reais.

**Gate:** relatório diferencia associação de causalidade; score apresenta fatores contribuintes; testes validam limites e comportamento em dados ausentes.

### Fase 5 — Power BI e Excel

**Objetivo:** entregar uma narrativa útil a operações e recrutadores.

**Implementar:** Power BI com Fleet Health, distribuição de risco, evolução temporal, top veículos, filtros por base/tipo; exportação `maintenance_report.xlsx` com Overview, Predictions, Recommendations e Statistics.

**Gate:** dashboard informa fonte/dados simulados e data de atualização; Excel abre sem fórmulas quebradas; cada visual responde a uma pergunta de negócio; screenshots e instruções de atualização no README.

### Fase 6 — Machine Learning e artefato Joblib

**Objetivo:** comparar baseline explicável com classificador de risco de manutenção em 30 dias.

**Implementar:** split temporal; pipeline Scikit-Learn; baseline Logistic Regression; Random Forest como candidato; validação temporal; `joblib` para modelo e metadados (`model_version`, features, métricas, janela); explicação por importâncias com limitações.

**Avaliação:** precisão, recall, F1, PR-AUC, matriz de confusão, taxa base e análise por veículo/tipo. Escolher limiar baseado em custo operacional simulado.

**Gate:** modelo vence ou justifica não vencer o baseline; conjunto de teste é posterior ao treino; inferência com feature ausente retorna erro compreensível; não há leakage; artefato é carregável em teste limpo.

### Fase 7 — FastAPI

**Objetivo:** disponibilizar uma interface pequena e auditável.

**Endpoints mínimos:**

```text
GET  /health
GET  /vehicles/{vehicle_id}
GET  /vehicles/{vehicle_id}/risk
GET  /fleet/health
POST /predictions
```

`POST /predictions` deve responder `risk_probability`, `risk_level`, `model_version`, `generated_at` e `top_factors`. A API não deve aceitar nem registrar PII.

**Gate:** OpenAPI disponível; testes de contrato para sucesso/422/404; `/health` verifica dependências sem expor segredos; requests e respostas de exemplo documentadas.

### Fase 8 — Docker Compose

**Objetivo:** uma execução local em comando único.

**Implementar:** serviços `postgres` e `api`; volumes explícitos; healthchecks; migrações/carga controladas; logs estruturados básicos. Serviço de ML só é separado se houver motivo demonstrado; inicialmente, o modelo pode estar na API.

**Gate:** `docker compose up --build` sobe ambiente limpo; API consulta banco; dados persistem em volume; documentação inclui parar/recriar e solução dos três erros mais prováveis.

### Fase 9 — Magalu Object Storage

**Objetivo:** representar um data lake simples e versionável na Magalu Cloud, aproveitando o Object Storage compatível com o ecossistema S3.

**Layout:**

```text
s3://<bucket>/raw/year=YYYY/month=MM/
s3://<bucket>/processed/year=YYYY/month=MM/
s3://<bucket>/models/<model-version>/
s3://<bucket>/reports/
```

**Implementar:** upload/download usando credenciais de menor privilégio; checksum/metadados; bloqueio de acesso público; configuração por variáveis de ambiente; documentação sem segredos no repositório.

**Gate:** arquivos raw nunca são sobrescritos; modelo aponta para versão imutável; política e consumo estimado dos créditos documentados; teste pode usar mock/local quando aplicável.

### Fase 10 — Magalu Cloud VM + Docker Compose

**Objetivo:** demonstrar deploy econômico e reproduzível do portfólio na Magalu Cloud.

**Implementar:** VM com Docker Compose, regras de rede mínimas, SSH por chave, variáveis fora do Git, backup/recuperação documentados e URL/healthcheck protegidos.

**Gate:** deploy reproduzível por runbook; porta do PostgreSQL não pública; API health verificada; desligamento/remoção e estimativa de consumo dos créditos documentados.

### Fase 11 — Magalu PostgreSQL DBaaS

**Objetivo:** migrar o PostgreSQL local para um serviço gerenciado sem alterar o contrato de dados do projeto.

**Implementar:** PostgreSQL DBaaS, conexão segura, migrações, variáveis de ambiente, política de backup/recuperação e comparação entre ambiente local e gerenciado.

**Gate:** API funciona contra o banco gerenciado; credenciais não aparecem no Git/logs; migrações são reproduzíveis; runbook de recuperação documentado.

### Fase 12 — Clojure Event Gateway

**Objetivo:** introduzir Clojure com responsabilidade pequena e justificável.

**Implementar:** endpoint `POST /events` que valida envelope, esquema, idempotency key e timestamp; encaminha evento válido para API/ingestão ou persiste quarentena. Não recriar ETL/ML em Clojure.

**Gate:** eventos duplicados são idempotentes; inválidos têm motivo e correlação; contrato JSON e testes de integração publicados; ADR justifica a fronteira de serviço.

### Fase 13 — Battery Intelligence

**Objetivo:** especializar elétricas sem comprometer suporte a combustão.

**Implementar:** health score sintético de bateria baseado em SOC, temperatura, tensão, ciclos e comportamento de carga; filtros por veículo elétrico; análises separadas; nulos corretos para combustão.

**Gate:** nenhuma métrica de bateria é aplicada à combustão; limiares são sinalizados como simulados; dashboard/API cobrem os dois tipos com contratos claros.

### Fase 14 — Integração SAP HANA + SAP Fiori (evolução enterprise)

**Objetivo:** demonstrar uma possível integração da plataforma com um ecossistema corporativo SAP sem transformar HANA/Fiori em dependências do MVP.

**SAP HANA:** receber dados consolidados, indicadores de manutenção e resultados de predição para cenários analíticos e de integração corporativa.

**SAP Fiori:** apresentar saúde da frota, alertas, risco de manutenção e processos operacionais em uma interface orientada a papéis.

**Critério arquitetural:** PostgreSQL continua como store operacional do MVP. HANA entra quando existir uma necessidade corporativa/analítica explícita. Fiori é camada de experiência e não substitui FastAPI, o modelo ML ou o armazenamento de dados.

**Gate:** diagrama de integração atualizado; contratos entre FleetGuard e SAP documentados; dados enviados são sintéticos/não pessoais; limitações de acesso, ambiente e licenciamento são registradas.

### Fase 15 — Observabilidade, segurança e arquitetura

**Objetivo:** tornar riscos e operação visíveis.

**Implementar:** logs JSON com `correlation_id`, métricas de requisição/erro/latência, alerta demonstrativo, readiness/liveness, rate limiting simples, validação de entrada, dependências fixadas, scan de segredos e revisão de acesso ao Object Storage/VM/DBaaS.

**Gate:** uma requisição pode ser rastreada ponta a ponta; dashboard/log permite identificar erro simulado; ameaça, controles e lacunas documentados; nenhum segredo aparece em histórico, logs ou exemplos.

## 9. ADRs obrigatórios

Nomeie como `docs/adr/NNNN-titulo.md`. Modelo:

```markdown
# ADR-NNNN: Título
Status: Accepted | Superseded
Data: YYYY-MM-DD
Contexto: problema e restrições.
Decisão: escolha feita.
Alternativas: opções descartadas e por quê.
Consequências: ganhos, custos, riscos e revisão futura.
```

| ADR | Decisão esperada |
|---|---|
| 0001 | PostgreSQL e modelo relacional inicial |
| 0002 | Dados sintéticos e contrato de simulação |
| 0003 | Split temporal e métricas de ML |
| 0004 | Modelo embarcado na API inicialmente |
| 0005 | Magalu Object Storage como data lake e convenção de paths |
| 0006 | Magalu Cloud VM + Docker Compose para demonstração |
| 0007 | Fronteira do gateway Clojure |
| 0008 | Segurança, retenção e dados não pessoais |
| 0009 | Magalu PostgreSQL DBaaS como banco gerenciado |
| 0010 | SAP HANA/Fiori como integração enterprise opcional |

## 10. Estratégia de testes

| Nível | Exemplos |
|---|---|
| Unitário | validação de schema, features, score, serialização |
| Dados | chaves únicas, ranges, monotonicidade, nulos por tipo |
| SQL | constraints, views, idempotência, resultados esperados |
| Integração | ETL→Postgres, API→modelo→banco, Compose |
| Contrato | schemas de request/response e gateway de eventos |
| Regressão | seed fixa, métricas mínimas e snapshot de features |
| Segurança | entradas inválidas, segredos, autorização S3 simulada |

Não medir cobertura apenas como porcentagem. Priorizar caminhos de decisão, validações e falhas que poderiam gerar um risco falso ou silencioso.

## 11. Perguntas de Grill-me

Use de 5 a 10 por fase, registre respostas curtas e marque o que exigiu estudo.

### Dados e domínio

- Qual diferença prática entre manutenção preventiva e preditiva neste produto?
- Por que `odometer_km` é monotônico e como você trata uma leitura menor?
- Por que uma janela móvel deve particionar por veículo?
- Como dados atrasados, duplicados e offline alteram o pipeline?

### Banco e SQL

- Por que o índice composto inclui veículo e timestamp?
- Quando uma window function é melhor que um `GROUP BY`?
- Como uma carga se mantém idempotente?

### ML

- Onde haveria data leakage neste dataset?
- Por que accuracy é insuficiente com evento raro?
- Qual custo simulado de falso negativo versus falso positivo?
- Por que o modelo não deve morar dentro do PostgreSQL?

### Arquitetura e operação

- Por que começar com monólito/API e não microserviços?
- O que muda se a frota crescer para 100 mil veículos?
- Para que serve o Object Storage, e o que continua no PostgreSQL?
- Como rastrear uma predição até dados e modelo que a geraram?
- O que justificaria migrar parte da camada analítica para SAP HANA?
- Qual responsabilidade pertence ao SAP Fiori e qual continua na API?
- Qual é a superfície de ataque do endpoint de eventos?

## 12. Prompts operacionais para OpenCode

### Iniciar uma fase

```text
Leia PROJECT_PLAN.md, README.md, docs/adr/ e o relatório da última fase.
Ative somente a Fase <NOME>. Não implemente itens futuros.
Produza primeiro um plano com objetivo, arquivos a alterar, contratos, riscos,
testes, evidências e ADRs. Em seguida faça 5–10 perguntas Grill-me específicas.
Espere minhas respostas/aprovação antes de implementar.
```

### Implementar após aprovação

```text
Implemente somente o plano aprovado da Fase <NOME>. Preserve dados e mudanças
existentes. Execute testes relevantes e faça uma revisão crítica do próprio diff.
Corrija falhas, atualize o relatório da fase e a documentação. Liste evidências
para cada critério de conclusão e pare aguardando aprovação humana; não avance.
```

### Continuar trabalho interrompido

```text
Retome a Fase <NOME>. Compare o estado atual com PROJECT_PLAN.md e o relatório
da fase. Diga em que passo do fluxo obrigatório estamos e quais gates faltam.
Não refaça etapas concluídas nem inicie a próxima fase. Teste antes de declarar
conclusão e registre qualquer desvio como decisão ou pendência.
```

### Transição de fase

```text
Audite a Fase <NOME> contra todos os critérios e a Definition of Done. Mostre
evidências, pendências, riscos e ADRs. Se qualquer item obrigatório falhar,
permaneça na fase e proponha correção. Somente após minha aprovação, crie o
plano e o Grill-me da Fase <PRÓXIMA>.
```

## 13. Roadmap de portfólio

| Marco | Resultado | Valor para vaga |
|---|---|---|
| MVP Dados (F0–F5) | EDA, SQL, modelo, BI/Excel | Analista/Engenharia de Dados júnior |
| MVP IA (F6–F8) | modelo, API e Compose | Dados/ML aplicado |
| Cloud (F9–F11) | Object Storage, VM, Docker e PostgreSQL DBaaS documentados | integração e deploy |
| Arquitetura (F12–F15) | eventos, bateria, SAP, segurança/observabilidade | AI Solutions Architect em evolução |

**Prioridade realista:** publicar F0–F8 antes de perseguir cloud/arquitetura avançada. Depois, usar os créditos da Magalu Cloud para F9–F11 e tratar Clojure e SAP como evoluções justificadas. Uma entrega menor, testada e explicável vale mais que uma arquitetura extensa sem funcionamento demonstrável.

## 14. README final — checklist de publicação

O README final deve conter:

- [ ] problema, público e aviso de dados/limiares simulados;
- [ ] arquitetura atual com diagrama e trade-offs;
- [ ] demonstração curta: gerar dados, subir ambiente, chamar API e abrir dashboard;
- [ ] modelo de dados e dicionário;
- [ ] resultados de EDA, SQL e ML com limitações;
- [ ] endpoints, exemplos de request/response e versão do modelo;
- [ ] instruções de testes, Docker e variáveis de ambiente;
- [ ] custos, segurança e observabilidade da versão Magalu Cloud;
- [ ] decisão arquitetural sobre PostgreSQL DBaaS;
- [ ] seção de integração SAP HANA/Fiori, caso implementada;
- [ ] ADRs e roadmap de próximos passos;
- [ ] seção “o que eu faria em produção”, diferenciada da implementação atual.

## 15. Critério final de sucesso

O FleetGuard AI está pronto para ser apresentado quando uma pessoa consegue, em poucos minutos: entender que os dados são sintéticos; gerar uma frota; ver análise e KPIs; consultar uma predição explicável por API; reproduzir o ambiente; e reconhecer as decisões arquiteturais, limites, custos e próximos passos sem promessas exageradas. A documentação deve diferenciar claramente o MVP, a infraestrutura Magalu Cloud e as integrações enterprise opcionais com SAP.

---

**Próxima ação autorizada:** iniciar apenas a Fase 0 usando o prompt “Iniciar uma fase”.
