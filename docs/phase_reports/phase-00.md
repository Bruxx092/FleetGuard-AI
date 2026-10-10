# Relatório da Fase 0 — Fundação e contrato

Status: **em andamento**. Este relatório registra as decisões tomadas nas rodadas de Grill-me antes da implementação. Conforme o ESTUDO_ARQUITETURA, o ADR-0002 será rascunhado pelo usuário (item NOVO).

## Decisões de colaboração (ESTUDO_ARQUITETURA)

- Classificação R4: boilerplate = REPETITIVO (agente implementa e testa); gerador, schema pandera, dicionário de dados e testes de dados = NOVO (guiado, sem entrega de código).
- ADR-0002: rascunho do usuário, crítica do agente depois.

## Decisões técnicas consolidadas (rodadas 1–3 do Grill-me)

### Fundação e tooling

- Repo: raiz em `/Users/pedrohenrique/Documents/FleetGuard`, remote `git@github.com:Bruxx092/FleetGuard.git`; histórico ramificado de `origin/main` (sem force).
- Tooling: `uv` (brew), Python 3.12 gerenciado pelo uv como interpretante dev; `requires-python >=3.12`; backend hatchling; nome `fleetguard` (projeto e pacote).
- Lint/format: ruff (config em `pyproject.toml`). Testes: pytest puro (sem pytest-cov na Fase 0).
- Validação de schema: pandera (runtime).
- Licença MIT; docs em PT-BR; código, commits (Conventional Commits) e valores sintéticos em EN; `.env.example` com `FLEETGUARD_LOG_LEVEL=INFO`.

### Gerador (contrato aprovado)

- CLI: `--seed --vehicles --days --electric-ratio --target-event-rate --output-dir` (nomes fixos `telemetry.csv` + `maintenance_events.csv`; desvio do exemplo do plano registrado aqui).
- Default Fase 0: seed 42, 20 veículos (7 elétricas com `BAT-0001..0007`, 13 combustão), 4 bases (`BASE-01..04`), IDs `VH-0001..0020`, 4 leituras/veículo/dia, 7 dias → 560 linhas; taxa-alvo ~15%.
- `risk_signal = 0.40·km_desde_último_evento + 0.30·desvio_temperatura + 0.30·taxa_eventos_bruscos` — 100% derivável dos CSVs emitidos (sem variáveis latentes; `oil_service_km` consistente com eventos). Eventos simulados até 30d além do horizonte da telemetria.
- Events: `event_id, vehicle_id, event_type ∈ {preventive, corrective, inspection}, occurred_at, odometer_km, notes` (EN); todos contam para `maintenance_label_30d`.
- Nulos: ~3% apenas em campos nullable do contrato; obrigatórios nunca nulos.
- Determinismo: decimais com 2 casas; timestamps ISO 8601 com `Z`; teste compara sha256 de duas execuções.
- Ranges simulados aprovados: speed 0–120 km/h; accel −5..5 m/s²; hard events 0–6/leitura; trip 5–120 min; engine temp 70–115 °C; rpm 800–9000; motor temp 40–110 °C; SOC 5–100%; battery temp 15–55 °C; voltage 45–72 V (48V); ciclos 0–1500.

### Checks de entendimento (obrigatórios do plano)

- UTC: elimina ambiguidade de fuso/DST; fuso local é apresentação.
- IDs sintéticos: privacidade por padrão; nenhuma PII/placa/vínculo com frotas reais.
- Reproducibilidade: seed + versão do gerador + precisão decimal fixa.

## Pendências (itens NOVO, guiados)

- [ ] Gerador `src/fleetguard/simulation/generate.py`
- [ ] Schema pandera (`schema.py`) e validação na geração
- [ ] `docs/data_dictionary.md`
- [ ] Testes de dados (determinismo sha256, SOC/odômetro, label↔eventos, monotonicidade, nulos)
- [ ] ADR-0002 (rascunho do usuário)
- [ ] Características arquiteturais em palavras do usuário (caps. 1–4 do livro) e quiz

## Evidências da fundação (REPETITIVO)

- `uv 0.13.0` instalado via brew; Python 3.12.15 pinned (`.python-version`).
- Ambiente: `uv sync` — pandas 3.0.6, numpy 2.5.4, pandera 0.34.1, pytest 9.1.1, ruff 0.17.0 (`uv.lock` commitado).
- Verificação: `uv run pytest` → 1 passed; `uv run ruff check .` e `uv run ruff format --check .` → clean.
- Nota: ruff configurado com `extend-exclude = ["*.md"]` para não reformatar blocos Python dos docs.
