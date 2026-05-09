# 🌾 Subcontinent AI-Agronomist
### **Intelligent Fertilizer Suggestive Tool & Nutrient Diagnostic Engine**
An advanced, AI-integrated decision-support system designed for the diverse agro-ecological zones of **Pakistan, India, and Bangladesh**. This tool bridges the gap between complex agronomic science and local farming practices by combining Large Language Models (LLMs) with a deterministic precision math engine.
## 🚀 Core Features
### **1. 🩺 Route 1: Plant Doctor (Diagnostics)**
 * **Symptom Mapping:** Analyzes visual plant cues (Chlorosis, Necrosis, Stunting) and their location (Old vs. New growth) to identify nutrient deficiencies.
 * **Environment Context:** Factors in regional soil types and moisture levels to differentiate between nutrient issues and environmental stress.
### **2. 🌾 Route 2: Yield Optimizer (Planning)**
 * **Custom Fertilizer Schedules:** Generates N-P-K recommendations based on target yield, growth stage, and previous crop history (e.g., nitrogen fixation from legumes).
 * **Micro-Region Intelligence:** Supports specific Agro-Ecological Zones (AEZs) rather than broad political boundaries for higher accuracy.
### **3. ⚖️ Precision Unit Localization (The Math Engine)**
 * **Zero-Hallucination Math:** Unlike standard AI, all unit conversions are handled by a hardcoded Python engine to ensure 100% mathematical accuracy.
 * **Local Units Supported:**
   * **Land:** Killa (Acre), Kanal, Bigha, Hectare.
   * **Weight:** Maund (Mann), 50kg Bags, Kilograms.
## 🛠️ Tech Stack
 * **Frontend:** Streamlit
 * **AI Engine:** Google Gemini 1.5 Flash
 * **Agentic Framework:** Google Antigravity
 * **Language:** Python 3.10+
## 📁 Repository Structure
```text
├── .streamlit/
│   └── secrets.toml.example  # Template for API configuration
├── app.py                    # Main application logic & UI
├── requirements.txt          # Project dependencies
├── .gitignore                # Security filters (protects private keys)
└── README.md                 # Documentation

```
## ⚙️ Setup & Installation
 1. **Clone the Repo:**
   ```bash
   git clone https://github.com/ahmaddevbuilds-oss/subcontinent-ai-agronomist.git
   
   ```
 2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   
   ```
 3. **Configure Secrets:**
   * Create a folder named .streamlit in the root directory.
   * Create a file named secrets.toml inside that folder.
   * Add your API key: API_KEY = "your_key_here"
 4. **Run App:**
   ```bash
   streamlit run app.py
   
   ```
## 🛡️ Safety & Disclaimer
*This tool is a demonstration of AI-integrated agricultural technology. Agricultural conditions vary by micro-location. Always verify AI recommendations with local soil tests and certified agronomists before large-scale application.*
## 👤 Author
**Ahmad Mumtaz**
*Agricultural Genetist & AI Workflow Architect *
Specializing in AI-driven automation for the Agricultural and Tech sectors.
