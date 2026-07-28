# Role 4: Core Developer / Integrator

## 1. Vai tro

Role 4 la nguoi lap rap san pham cuoi cung cua nhom. Nhiem vu chinh la tich hop cac phan do Role 1, Role 2 va Role 3 tao ra vao `src/app.py`, sau do chay thu, debug va dam bao demo Chatbot vs ReAct Agent hoat dong on dinh.

File phu trach chinh:

- `src/app.py`
- Doc ho tro: `docs/ROLE_4_CORE_DEVELOPER_INTEGRATOR.md`

File can doc va tich hop:

- `config/test_cases.json` tu Role 1
- `src/tools.py` tu Role 2
- `src/prompts.py` tu Role 3
- `src/providers.py` co san trong project
- `docs/trace_eval.md` tu Role 5 de doi chieu ket qua

## 2. Muc tieu dau ra

Den cuoi lab, Role 4 can dam bao app co the:

- Load duoc toan bo test cases tu `config/test_cases.json`.
- Khoi tao duoc LLM provider bang `get_llm_provider()`.
- Chay duoc baseline chatbot qua `run_baseline_chatbot()`.
- Chay duoc ReAct Agent qua `run_react_agent()`.
- Agent co the goi tool tu `AVAILABLE_TOOLS`.
- Agent xu ly duoc cac loi Parser Error, Unknown Tool va Tool Exception.
- Agent dung lai bang `Final Answer` hoac safe fallback khi vuot `MAX_ITERATIONS`.
- In trace ro rang theo chuoi `Thought -> Action -> Observation -> Final Answer`.

## 3. Checklist theo tung moc

### Moc 1: Kiem tra moi truong

- [ ] Chay lenh:

```bash
python src/app.py
```

- [ ] Xac nhan app khong loi import.
- [ ] Xac nhan provider duoc khoi tao thanh cong.
- [ ] Xac nhan app doc duoc `config/test_cases.json`.
- [ ] Bao lai nhom neu thieu bien moi truong hoac file cua role khac.

### Moc 2: Tich hop Baseline Chatbot

- [ ] `git pull` de lay code moi nhat cua Role 1, Role 2 va Role 3.
- [ ] Kiem tra `CHATBOT_BASELINE_PROMPT` trong `src/prompts.py`.
- [ ] Kiem tra danh sach cau hoi trong `config/test_cases.json`.
- [ ] Hoan thien `run_baseline_chatbot(user_query, provider)`.
- [ ] Baseline chatbot chi goi LLM, khong goi tool.
- [ ] Chay it nhat 1 cau simple va 1 cau can tool de Role 5 ghi nhan su khac biet.

### Moc 3: Tich hop ReAct Agent

- [ ] `git pull` de lay prompt va tools moi nhat.
- [ ] Kiem tra `REACT_SYSTEM_PROMPT` va `MAX_ITERATIONS`.
- [ ] Kiem tra `AVAILABLE_TOOLS` trong `src/tools.py`.
- [ ] Tao parser doc output cua LLM theo format:

```text
Thought: ...
Action: tool_name[arg1, arg2]
Final Answer: ...
```

- [ ] Neu gap `Action`, tach `tool_name` va arguments.
- [ ] Neu tool khong ton tai trong `AVAILABLE_TOOLS`, tra ve observation dang loi.
- [ ] Neu tool bi exception, bat loi va dua loi vao `Observation`.
- [ ] Sau moi `Observation`, append vao lich su hoi thoai de LLM suy luan tiep.
- [ ] Neu gap `Final Answer`, dung loop va in cau tra loi cuoi.
- [ ] Neu vuot `MAX_ITERATIONS`, dung loop va tra safe fallback.

### Moc 4: Regression va demo

- [ ] Chay toan bo test cases trong `config/test_cases.json`.
- [ ] Xac nhan cau simple co the di theo chatbot path.
- [ ] Xac nhan cau multi-step co the goi 1 tool.
- [ ] Xac nhan cau multi-tool co the goi nhieu tool neu prompt yeu cau.
- [ ] Xac nhan edge case khong lam app crash.
- [ ] Gui trace cho Role 5 de cap nhat `docs/trace_eval.md`.
- [ ] Chuan bi noi dung demo kien truc cho phan trinh bay.

## 4. Hop dong tich hop voi cac role khac

Role 1 can cung cap:

- `config/test_cases.json` dung JSON hop le.
- Moi test case nen co `id`, `category`, `question`, `expected_behavior`.

Role 2 can cung cap:

- Cac tool trong `src/tools.py`.
- Dictionary `AVAILABLE_TOOLS`.
- Tool tra ve string ro rang, khong nen crash truc tiep khi input sai.

Role 3 can cung cap:

- `CHATBOT_BASELINE_PROMPT`.
- `REACT_SYSTEM_PROMPT`.
- `MAX_ITERATIONS`.
- Format output thong nhat de parser cua Role 4 doc duoc.

Role 5 can cung cap:

- Ket qua quan sat chatbot baseline.
- Trace cua ReAct Agent.
- Cac loi hoac hanh vi la de Role 4 fix truoc demo.

## 5. Yeu cau ky thuat cho `src/app.py`

Nen co cac ham/chuc nang sau:

- `load_test_cases()`: doc file test case.
- `run_baseline_chatbot(user_query, provider)`: chay chatbot thuong.
- `parse_react_output(response)`: tach `Thought`, `Action`, `Final Answer`.
- `execute_tool(tool_name, args)`: goi tool an toan tu `AVAILABLE_TOOLS`.
- `run_react_agent(user_query, provider)`: chay vong lap ReAct.
- `main`: khoi tao provider, load tests va chay demo.

Khong nen:

- Hard-code rieng mot cau hoi demo.
- Hard-code rieng thanh pho `Ha Noi` trong ReAct loop.
- Goi truc tiep `get_weather()` hoac `search_flights()` trong agent loop neu co the dispatch qua `AVAILABLE_TOOLS`.
- De app crash khi LLM tra format sai.

## 6. Lenh lam viec nhanh

Lay code moi nhat:

```bash
git pull
```

Chay app:

```bash
python src/app.py
```

Commit phan Role 4:

```bash
git add src/app.py docs/ROLE_4_CORE_DEVELOPER_INTEGRATOR.md
git commit -m "Role 4: core integration"
git push
```

## 7. Tieu chi hoan thanh

- [ ] `python src/app.py` chay duoc tu dau den cuoi.
- [ ] Baseline chatbot va ReAct Agent deu co output rieng.
- [ ] ReAct Agent in duoc trace `Thought`, `Action`, `Observation`.
- [ ] Unknown tool khong lam crash app.
- [ ] Tool exception khong lam crash app.
- [ ] Agent co guardrail dung sau `MAX_ITERATIONS`.
- [ ] Role 5 co du trace de viet bao cao.
- [ ] Nhom co the demo app tu terminal.

## 8. Noi dung trinh bay cua Role 4

Khi demo, Role 4 nen noi ngan gon theo thu tu:

1. App doc test cases tu `config/test_cases.json`.
2. Baseline chatbot chi dung LLM nen han che voi cau hoi can du lieu/tool.
3. ReAct Agent dung prompt de sinh `Thought` va `Action`.
4. `src/app.py` parse action, tim tool trong `AVAILABLE_TOOLS`, chay tool va dua ket qua ve thanh `Observation`.
5. Agent lap lai den khi co `Final Answer` hoac cham `MAX_ITERATIONS`.
6. Guardrails giup app khong crash va khong lap vo han.
