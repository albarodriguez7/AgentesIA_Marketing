# Lead qualification agent with LangGraph

🇪🇸 [Español](README.md) · 🇬🇧 **English**

An AI agent that researches a company's website, extracts verifiable data and decides whether it is a good potential client for a marketing agency specialised in local businesses in Madrid.

---

## The problem

A marketing agency receives leads every day: someone downloads a guide, requests an audit or subscribes to the newsletter. Qualifying them by hand means visiting each company's website, finding out what it does, where it is and how many locations it has, and deciding whether it is worth contacting. It is repetitive work that can take several minutes per lead.

This agent does it automatically, in a few seconds and for less than one cent per lead.

## Example

**Input:**
```
Web: https://clinicaceodent.es/. Ha descargado nuestra guía de SEO local.
```
*(The lead downloaded our local SEO guide.)*

**What the agent does:** it visits the home page, decides on its own which other pages are likely to contain the missing information (contact, about the clinic), and summarises what it found by copying the evidence literally from the website:

```
SECTOR: Clínica dental, odontología integral, ortodoncia, implantes...
CIUDADES CON SEDES: Madrid
NÚMERO DE SEDES SEGÚN LA WEB: no aparece
DIRECCIONES ENCONTRADAS: Av. de San Luis, 54 (Esq. Luis Buitrago) 28033 Madrid
DATOS NO CONFIRMADOS: número exacto de sedes
```
*(Sector: dental clinic · Cities with locations: Madrid · Number of locations stated on the website: not found · Addresses found: one in Madrid · Unconfirmed: exact number of locations.)*

**Result:**
```
Datos: sector='salud' numero_sedes=1 en_madrid=True intencion='media'
Puntuación: 7 → nutrir
```
*(Health sector, 1 location, in Madrid, medium intent → score 7 → nurture.)*

---

## How it works

The agent is a LangGraph graph built node by node:

```mermaid
flowchart TD
    START([Start]) --> investigar
    investigar -->|requests a page| herramientas
    herramientas --> investigar
    investigar -->|evidence-based summary| extraer
    extraer --> puntuar
    puntuar --> END([End])
```

| Node | What it does | Uses AI? |
|---|---|---|
| `investigar` (research) | Decides which page to read next or writes the final evidence-based summary | Yes |
| `herramientas` (tools) | Downloads the page and returns its text and links | No |
| `extraer` (extract) | Turns the summary into structured data (Pydantic) | Yes |
| `puntuar` (score) | Applies the business rules and decides the action | No |

---

## Design decisions

**The AI extracts, the code decides.** AI is only used for what it does better than code: understanding messy text. Scoring and the final decision are Python rules: always consistent, explainable point by point, free to run and covered by tests. Changing a business criterion means changing a number, without touching the agent.

**Evidence instead of conclusions.** Instead of asking the AI "how many locations does it have?", it is asked to literally copy the addresses or the sentence on the website that states it. If it finds nothing, it must say "not found" rather than infer it. This stopped the agent from asserting data with little evidence (for example, "1 location" after reading only the home page).

**Ask only for the data the decision needs.** An early rule that counted addresses failed with a chain of more than 380 gyms (it said "1 location"). Since the decision only needs to know the range of locations, the definition of evidence was broadened: a statement from the company itself is worth more than counting addresses.

**Important limits live in the code.** The maximum number of pages per lead does not depend on the AI "obeying" the instructions: when the limit is reached, the code removes its ability to use tools (`tool_choice="none"`).

**One job per node.** `investigar` and `extraer` are separate. `extraer` only reads the final summary, not the full pages, which greatly reduces the number of tokens.

### Business rules (ideal customer profile)

| Criterion | Points |
|---|---|
| **Requirement:** having a location in Madrid | If not → 0 points and discard |
| Sector: health, beauty, hospitality or education | +3 |
| Location in Madrid | +2 |
| Between 2 and 10 locations | +2 |
| High / medium / low intent | +3 / +2 / +0 |

**8 or more → contact · 5 to 7 → nurture · below 5 → discard**

The 10-location cap exists because a very large chain usually has its own marketing department and is not the ideal client for a local agency.

---

## Quality

### Tests for the rules
16 `pytest` tests that check scoring and decisions, including edge cases (the boundaries between actions, unknown number of locations, the 10-location cap, leads outside Madrid). They run in under a second and at no cost.

### Agent evaluation
A LangSmith dataset with 6 real leads and the correct answer verified by hand, chosen to cover different cases: one location, small chain, very large chain, outside Madrid, hospitality and a home-visit business. Four evaluators check the sector, the location, the range of locations and the final action separately.

| Metric | Result |
|---|---|
| Accuracy | 6 out of 6 on all four evaluators |
| Approximate cost | ~$0.005 per lead (GPT-4.1 mini) |
| Time | 5 to 10 seconds per lead |

Something I learned by measuring: around **97% of the tokens are input tokens**, because the whole conversation is resent on every turn of the agent loop. Cost also varies noticeably between runs of the same agent, so comparing versions requires several runs.

### A complete improvement cycle
The dataset itself revealed a flaw in the rules: a language school in Barcelona was classified as "contact" for a Madrid agency. It was fixed as follows:
1. **Test** describing the desired behaviour (fails).
2. **Code:** a guard clause in the scoring function (tests pass).
3. **Dataset** updated with the new correct answer.
4. **Evaluation** of the new version, compared with the previous one in LangSmith, checking that only the expected results changed.

---

## Tech stack

Python 3.13 · LangChain · LangGraph · OpenAI (GPT-4.1 mini) · Pydantic · LangSmith (tracing and evaluation) · pytest · Requests · BeautifulSoup · Poetry

---

## Project structure

```
├── leads/                      ← lead qualification agent
│   ├── agente_grafo.py         ← the agent (LangGraph graph)
│   ├── evaluar_lead.py         ← data schema and business rules
│   └── evaluaciones/           ← LangSmith dataset and evaluation
├── auditoria/                  ← acquisition audit agent (in progress)
├── compartido/
│   └── herramientas.py         ← web reading tool, shared by the agents
├── tests/                      ← tests for the rules
└── ejemplos/                   ← learning scripts and a create_agent version (for comparison)
```

*The code, prompts and data are in Spanish, as the agent targets Spanish businesses.*

---

## Installation and usage

**Requirements:** Python 3.11 or later, Poetry, an OpenAI API key and, optionally, a LangSmith API key.

```bash
git clone https://github.com/albarodriguez7/AgentesIA_Marketing.git
cd AgentesIA_Marketing
poetry install
```

Copy `.env.example` to `.env` and fill in your keys.

| I want to... | Command |
|---|---|
| Qualify an example lead | `poetry run python agente_grafo.py` |
| Run the tests | `poetry run pytest` |
| Run the evaluation (requires LangSmith) | `poetry run python -m evaluaciones.evaluar_agente` |

---

## Next steps

- Reduce cost by removing the repeated text (menus and links) resent on every turn, and measure the savings with the dataset.
- Have `investigar` return its summary as structured data instead of labelled text.
- Grow the evaluation dataset with every real case where the agent fails.
- Next modules of the platform: acquisition audit, metrics and retention.

---

## Author

Project developed as part of my training as an AI Engineer.

- LinkedIn: [my profile](https://www.linkedin.com/in/albarodriguezperales/)
- GitHub: [my projects](https://github.com/albarodriguez7)
