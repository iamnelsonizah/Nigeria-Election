# Nigeria Election Analytics Dashboard

A full-stack election analytics workspace built with a Next.js dashboard frontend and a FastAPI analytics backend. It covers Nigerian presidential, gubernatorial, National Assembly, turnout, regional, and anomaly indicators across the 2011-2023 election cycles.

## Stack

- **Frontend:** Next.js App Router, React, TypeScript, custom responsive chart components
- **Backend:** FastAPI, Pandas, NumPy, typed analytics service layer
- **Data:** In-repository election datasets and curated helper module in `data/`

## Features

| Area | Coverage |
| --- | --- |
| Overview | National KPIs, 2023 vote share, turnout trend, winners timeline |
| Presidential | National result, state-level vote stacks, party wins, state table |
| Vote trends | Party vote share and absolute vote trajectories |
| Regional | Geopolitical zone summaries, dominant party signals, state drilldowns |
| Turnout | Registration, votes cast, non-voting gap, state and zone turnout |
| National Assembly | Senate and House composition with trend lines |
| Governorship | 2023 state executive control and winning vote totals |
| Anomalies | Benford analysis, turnout outliers, margin spikes, known incident context |

## Project Structure

```text
nigeria_election_dashboard/
├── backend/
│   └── app/
│       ├── main.py
│       ├── routes.py
│       └── services/election_analytics.py
├── frontend/
│   └── src/
│       ├── app/
│       ├── components/
│       └── lib/
├── data/
│   ├── nigeria_election_data.py
│   └── *.csv
├── requirements.txt
└── package.json
```

## Setup

Create and install the Python backend dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install the frontend dependencies:

```powershell
npm.cmd --prefix frontend install
```

## Run Locally

Start FastAPI from the project root:

```powershell
npm.cmd run api
```

Build and start the verified Next.js frontend in another terminal:

```powershell
npm.cmd run build
npm.cmd run start
```

Open the dashboard at [http://127.0.0.1:3000](http://127.0.0.1:3000). The API docs are available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

For hot-reload frontend development, use:

```powershell
npm.cmd run dev
```

## Configuration

The Next.js proxy reads `FASTAPI_URL` from `frontend/.env.local`. If omitted, it defaults to:

```text
http://127.0.0.1:8000
```

FastAPI CORS origins can be overridden with `CORS_ORIGINS`.

## Validation

Useful checks:

```powershell
npm.cmd --prefix frontend run lint
npm.cmd --prefix frontend run build
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

## Disclaimer

The anomaly module surfaces statistical flags for civic research and review. These signals are not legal evidence of electoral fraud.
