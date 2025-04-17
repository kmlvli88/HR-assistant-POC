#  HR 假勤 AI 助理（POC 專案）

本專案為企業內部 HR 應用場景的 AI 助理 POC。  
透過 LlamaIndex + 本地 Mistral 模型，實作一個可查詢請假規定、計算剩餘假別、回答簽核對象的 AI 機器人，並結合 Streamlit 作為前端互動介面。


# 專案背景

驗證企業內部可否透過 AI 助理查詢 HR 請假規則、簽核流程與員工假勤狀態。
並希望評估導入 HR助理是否能：
•	減少 HR 回覆負擔
•	提升同仁對規則的掌握度
•	整合多來源資料（PDF、JSON）

---

## 驗證內容

✅ 語意檢索 PDF 檔案（請假規定 / 簽核流程）  
✅ 根據員工年資與已休天數，自動推算剩餘特休  
✅ 查詢固定假別（事假、婚假、病假等）規則  
✅ 自動辨識簽呈問題，回覆簽核對象  
✅ 本地部署（Ollama），保障資料隱私  
✅ 前端使用 Streamlit 提供自然對話介面

---

##  使用技術

| 技術           | 用途                              |
|----------------|-----------------------------------|
| Python         | 程式撰寫語言                       |
| Streamlit      | 前端對話介面框架                   |
| LlamaIndex     | 語意檢索引擎框架（RAG）                 |
| SentenceSplitter | PDF chunk 切割模組               |
| FAISS          | 向量索引儲存（內建於 LlamaIndex）  |
| HuggingFace Embedding | 向量模型（MiniLM）           |
| Ollama + Mistral | 本地大型語言模型                 |

---

##  專案結構

```bash
├── app.py                ← 主程式
├── data/
│   ├── leave_policy.pdf  ←勤假規則(公司規則不方便對外公開)
│   ├── approval_flow.pdf ←簽呈規則(公司規則不方便對外公開)
│   └── employees.json    ←員工資訊
├── requirements.txt      
└── README.md

## 資料流程圖


![資料流程圖](https://i.imgur.com/mwfiLrz.png)





## 驗證及果
![image](https://github.com/user-attachments/assets/589b2610-49c6-4bf3-a399-a8356024b89e)


## 價值與效益
•	減少 HR  重工（主管可直接查詢）
•	提升同仁 規則掌握度
•	整合多來源資料（PDF、員工系統）
•	完全私有部署（Ollama 本地推理）

## 後續建議與延伸方向
擴充功能:增加API接口，實現AI AGENT(例如:使用LangChain框架達到自動化請假流程)
MCP 協議:為 AI 模型提供了一個標準化的方式來連接不同的數據源和工具。
![image](https://github.com/user-attachments/assets/7bb0a0c0-dfb3-44c6-a880-0fc3f0ec138b)

資料來源 : https://modelcontextprotocol.io/introduction
