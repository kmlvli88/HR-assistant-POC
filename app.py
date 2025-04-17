import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path

import streamlit as st
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 初始化模型與嵌入器
llm = Ollama(model="mistral", temperature=0.7, request_timeout=300)
embedding = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 路徑設定
base_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()
data_path = base_path / "data"
employee_path = data_path / "employees.json"

# 向量資料建立
splitter = SentenceSplitter(chunk_size=500, chunk_overlap=50)
leave_docs = SimpleDirectoryReader(input_files=[str(data_path / "leave_policy.pdf")]).load_data()
sign_docs = SimpleDirectoryReader(input_files=[str(data_path / "approval_flow.pdf")]).load_data()

leave_nodes = splitter.get_nodes_from_documents(leave_docs)
sign_nodes = splitter.get_nodes_from_documents(sign_docs)

leave_index = VectorStoreIndex(leave_nodes, llm=llm, embed_model=embedding)
sign_index = VectorStoreIndex(sign_nodes, llm=llm, embed_model=embedding)

leave_query = leave_index.as_query_engine(similarity_top_k=6, llm=llm)
sign_query = sign_index.as_query_engine(similarity_top_k=6, llm=llm)

# 假別設定
VACATION_TYPES = {
    "特休": {"type": "year_by_seniority"},
    "事假": {"type": "fixed", "limit": 14},
    "病假": {"type": "rule_only"},
    "婚假": {"type": "rule_only"},
    "喪假": {"type": "rule_only"}
}

# 讀取員工資料
with open(employee_path, "r", encoding="utf-8") as f:
    employees = json.load(f)

# 工具函式
def extract_vacation_type(text):
    for v in VACATION_TYPES:
        if v in text:
            return v
    return None

def calc_years(join_date_str):
    join_date = datetime.strptime(join_date_str, "%Y-%m-%d")
    return relativedelta(datetime.today(), join_date).years

def is_signing_question(text):
    return "誰" in text and ("簽" in text or "核准" in text or "簽核" in text)

def is_policy_question(text):
    return any(x in text for x in ["怎麼請", "如何請", "請假方式", "休幾天", "規定", "申請辦法"])

# Streamlit UI 初始化
st.set_page_config(page_title="HR 假勤助理", page_icon="🧑‍💼")
st.title("🧑‍💼 HR 假勤助理（支援請假規定 / 剩餘假 / 簽核流程）")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

question = st.text_input("請輸入你的問題")

if question:
    st.session_state.chat_history.append({"role": "user", "text": question})
    vacation_type = extract_vacation_type(question)
    employee = next((e for e in employees if e["name"] in question), None)

    # ✅ 簽核問題
    if is_signing_question(question):
        result = sign_query.query(f"""
你是公司 AI 助理，請依據簽呈規則回答：{question}
只能根據提供的簽核條文回答，若查不到請說「查無明確規則」。
""")
        st.session_state.chat_history.append({"role": "assistant", "text": str(result)})

    # ✅ 假別規定說明
    elif is_policy_question(question) or (vacation_type and not employee):
        rule = leave_query.query(f"請說明公司 {vacation_type} 的請假規定")
        st.session_state.chat_history.append({"role": "assistant", "text": str(rule)})

    # ✅ 查詢剩餘假
    elif vacation_type and employee:
        emp_name = employee["name"]
        join_date = employee.get("join_date")
        used = employee["used"].get(vacation_type, 0)
        vac_config = VACATION_TYPES[vacation_type]

        if vac_config["type"] == "year_by_seniority":
            if not join_date:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "text": "⚠️ 員工資料缺少入職日，無法計算年資"
                })
            else:
                years = calc_years(join_date)
                rule_text = leave_query.query(f"請提供公司請假政策中，年資 {years} 年的員工特休天數")
                prompt = f"""
公司特休規定如下：{rule_text}
{emp_name} 的年資為 {years} 年，已休特休：{used} 天。
請計算剩餘特休天數，格式如下：
- 年資：X 年
- 可休特休：X 天
- 已休特休：X 天
- 剩餘特休：X 天
"""
                response = leave_query.query(prompt)
                st.session_state.chat_history.append({"role": "assistant", "text": str(response)})

        elif vac_config["type"] == "fixed":
            limit = vac_config["limit"]
            remain = limit - used
            rule = leave_query.query(f"請說明公司 {vacation_type} 的請假規定")
            summary = f"- 可休{vacation_type}：{limit} 天\n- 已休{vacation_type}：{used} 天\n- 剩餘{vacation_type}：{remain} 天"
            final_response = f"{rule}\n\n{summary}"
            st.session_state.chat_history.append({"role": "assistant", "text": final_response})

        elif vac_config["type"] == "rule_only":
            rule = leave_query.query(f"請說明公司 {vacation_type} 的請假規定")
            st.session_state.chat_history.append({"role": "assistant", "text": str(rule)})

    else:
        st.session_state.chat_history.append({
            "role": "assistant",
            "text": "請確認問題是否包含員工姓名與假別，或請明確詢問規則 / 剩餘假 / 簽核流程"
        })

# 渲染聊天歷程
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"👤 **你**：{chat['text']}")
    else:
        st.markdown(f"🤖 **助理**：{chat['text']}")
