# Chay backend va frontend

## 1. Cai dependencies

Tu thu muc goc:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd src\frontend
npm install
```

## 2. Chay backend

Tu thu muc goc:

```powershell
$env:LLM_PROVIDER = "mock"
.\.venv\Scripts\python.exe src\app.py --serve
```

Backend mac dinh chay tai `http://localhost:8000`.

- Health: `GET http://localhost:8000/api/health`
- Tool registry: `GET http://localhost:8000/api/tools`
- API docs: `http://localhost:8000/docs`

## 3. Chay frontend

Mo terminal khac:

```powershell
cd src\frontend
npm run dev
```

Frontend doc `VITE_API_BASE_URL` tu `.env` va mac dinh ket noi den
`http://localhost:8000/api`.

## Demo fixture

Backend dung `USR001` lam nguoi dung demo mac dinh de cac tool consent-aware co
the doc synthetic dataset. Co the doi bang bien moi truong:

```powershell
$env:CUPID_DEMO_USER_ID = "USR001"
```
