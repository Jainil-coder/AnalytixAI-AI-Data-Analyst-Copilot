# AnalytixAI - AI Data Analyst Copilot

**Ask. Analyze. Discover.**

AnalytixAI is an AI-powered data analysis application that helps users explore datasets, perform exploratory data analysis (EDA), and generate meaningful insights using natural-language questions.

Instead of manually writing Python queries or building charts, users can upload a CSV file, ask questions in plain English, and let InsightOS analyze the data, generate visualizations, and explain the findings.

---

## 🚀 Key Features

### 1. CSV Data Upload
- Upload and analyze CSV datasets.
- Preview uploaded data.
- Inspect dataset dimensions, columns, and data types.
- View essential dataset statistics.

### 2. Automated Exploratory Data Analysis (EDA)
Automatically explore datasets through:
- Descriptive statistics.
- Missing-value analysis.
- Duplicate record detection.
- Correlation analysis.
- Distribution analysis.
- Outlier detection.
- Data visualization.

### 3. Natural Language Data Analysis
Ask questions about your dataset using everyday language.

For example:
- What are the key trends in this dataset?
- Which factors have the strongest relationship with the target variable?
- Are there any unusual values or outliers?
- Which categories have the highest average values?
- How has performance changed over time?

AnalytixAI interprets the question and determines the appropriate analysis to perform.

### 4. AI-Powered Analysis with Gemini
- Uses Google's Gemini API to understand user questions.
- Converts natural-language requests into structured analysis plans.
- Uses Python-based data processing to calculate actual results.
- Generates explanations based on computed results.

### 5. Data Visualization
Generate visualizations to make patterns easier to understand:
- Histograms.
- Box plots.
- Bar charts.
- Line charts.
- Scatter plots.
- Correlation heatmaps.

### 6. Statistical Analysis
Perform common analytical operations, including:
- Group-by aggregations.
- Mean, sum, and count calculations.
- Value frequency analysis.
- Correlation analysis.
- IQR-based outlier detection.

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| AI / LLM | Google Gemini |
| Data Processing | Pandas, NumPy |
| Data Visualization | Matplotlib, Seaborn, Plotly |
| Data Format | CSV |
| AI Integration | Google Gen AI SDK |

---

## 🏗️ Project Structure

```text
AnalytixAI/
│
├── app.py
├── config.json
├── requirements.txt
├── .gitignore
│
└── utils/
    ├── __init__.py
    ├── gemini_client.py
    ├── analysis_engine.py
    └── prompts.py
```

### File Responsibilities

| File | Responsibility |
|---|---|
| `app.py` | Streamlit application and user interface |
| `config.json` | Local Gemini API configuration |
| `requirements.txt` | Python dependencies |
| `gemini_client.py` | Gemini API integration |
| `analysis_engine.py` | Data processing, statistical analysis, and chart generation |
| `prompts.py` | AI system instructions and analysis prompts |

---

## ⚙️ Installation and Setup

### Prerequisites

Make sure you have the following installed:

- Python 3.11
- pip
- Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/InsightOS.git
```

Navigate into the project directory:

```bash
cd InsightOS
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

For macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Gemini API Key

Create a `config.json` file in the project root:

```json
{
    "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY"
}
```

Replace `YOUR_GEMINI_API_KEY` with your actual API key.

You can obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

**Security:** Never commit your API key or `config.json` to GitHub. Keep `config.json` in `.gitignore`.

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser, usually at:

```text
http://localhost:8501
```

---

## 💡 Example Use Case

Consider a vehicle sales dataset containing information such as vehicle make, model, year, condition, mileage, market value, and selling price.

A user can upload the dataset and ask:

**"Which vehicle manufacturers have the highest average selling prices, and how does mileage affect their resale value?"**

InsightOS can:
1. Understand the analytical question.
2. Identify the relevant dataset columns.
3. Create an analysis plan.
4. Execute the required calculations using Python.
5. Generate relevant visualizations.
6. Explain the findings in natural language.

This makes data exploration more accessible to users without requiring them to write code.

---

## 🔐 Security Considerations

- Keep API keys out of source control.
- Add configuration files containing secrets to `.gitignore`.
- Validate uploaded datasets before processing.
- Avoid executing arbitrary code generated by an LLM.
- Use controlled, predefined analytical operations wherever possible.

---

## 🔮 Future Enhancements

Potential improvements for future versions include:

- [ ] Support for Excel files and additional data formats.
- [ ] Database connectivity (PostgreSQL, MySQL, etc.).
- [ ] Advanced multi-step AI data analysis.
- [ ] Interactive dashboards.
- [ ] Automated report generation in PDF and Excel.
- [ ] Conversational memory for follow-up analytical questions.
- [ ] Multiple dataset comparison.
- [ ] Advanced statistical and predictive analysis.
- [ ] Data cleaning recommendations and automated transformations.
- [ ] User authentication and role-based access.
- [ ] Deploy the application for public access.

---

## 🎯 Project Vision

InsightOS aims to make data analysis accessible to everyone.

The long-term vision is to evolve from a CSV-based AI analytics assistant into an intelligent data analysis platform that can connect to multiple data sources, understand complex business questions, perform multi-step analysis, and deliver actionable insights.

**Ask. Analyze. Discover.**

---

## 👨‍💻 Author

**Jainil Shah**

GitHub: [Jainil-coder](https://github.com/Jainil-coder)

---

*Built with Python, Streamlit, and Google Gemini.*
