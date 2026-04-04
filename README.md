# AgroAnalítica IFRO

Dashboard de análise climatológica e agronômica da Estação Meteorológica IFRO — Colorado do Oeste · RO.

## Estrutura do Repositório

```
agroanalytica_ifro/
├── app.py                    # Aplicação Streamlit principal
├── Dados2024atéhoje.csv      # Dados da estação (NÃO compartilhar publicamente)
├── requirements.txt          # Dependências Python
└── README.md
```

## Funcionalidades

- **Visão Geral** — KPIs e série histórica completa
- **Temperatura & GDD** — Graus-dia, amplitude térmica, janelas móveis
- **Radiação Solar** — Energia acumulada 45 dias, ET, correlações
- **Balanço Hídrico** — P × ET mensal, chuva acumulada 30d
- **Janela de Plantio** — Cálculo de mês ideal por cultura (Soja, Milho, Feijão, Café, Mandioca)
- **Dados Brutos** — Tabela navegável com export CSV

## Deploy no Streamlit Cloud

1. Suba este repositório no GitHub como **privado**
2. Acesse https://share.streamlit.io
3. Conecte sua conta GitHub
4. Selecione este repositório → branch `main` → arquivo `app.py`
5. Clique em **Deploy**

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```
