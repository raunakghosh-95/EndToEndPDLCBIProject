# EndToEndPDLCBIProject
## 📌 Overview  
AI-Powered End 2 End PDLC BI Project: A Streamlit web app that uses OpenAI to automatically generate Business Requirements Documents (BRD), system design artifacts (e.g., UML diagrams, ER diagrams), and Copilot-ready Power BI dashboard development guides from input files or text. Supports custom templates, enhancements, and document exports.
This repository provides a complete **Business Intelligence (BI) project framework** modeled on the Software Development Life Cycle (SDLC).  
Each phase (Planning → Requirements → Design → Development → Testing → Deployment) highlights:  

- **Inputs** (what you start with)  
- **Outputs** (deliverables/documents/artifacts)  
- **Transformation tools** (AI, Python libraries, BI platforms)  

The framework integrates modern AI tools (OpenAI, LangChain, Ollama), Python libraries (Pandas, SpaCy, Python-docx, Streamlit, PlantUML), and BI technologies (Power BI, Microsoft Copilot, Microsoft Fabric) to **automate and accelerate BI project delivery**.  

---

## ⚙️ Key Features  
- End-to-end BI pipeline automation  
- Modular **Master Application** with:  
  - BRD Generator  
  - System Design Generator  
  - Dashboard Development Doc Generator  
  - Power BI Dashboard Section  
- AI/LLM integration for document generation and enrichment  
- Streamlit UI for interactive workflows  
- Power BI + Microsoft Copilot + Fabric for final deployment  

---

## 🛠️ Tech Stack  
- **Python Libraries:** Pandas, SpaCy, Python-docx, Streamlit, LangChain, Ollama  
- **Visualization & Design:** PlantUML, Mermaid  
- **AI Tools:** OpenAI API, Grok AI  
- **BI Tools:** Power BI, Microsoft Copilot, Microsoft Fabric  

---

## 📂 Project Structure  
```plaintext
├── brd_generator/            # BRD generation scripts
├── system_design_generator/  # UML/data model generator
├── dashboard_generator/      # Dashboard design doc generator
├── powerbi_section/          # Power BI integration scripts
├── tests/                    # Testing logic
├── examples/                 # Sample input/output docs
├── requirements.txt
├── README.md
└── .env.example              # API key placeholders
