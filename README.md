# 🔍 Neo4j Query Generator with OpenAI & File Upload

## 🚀 Overview
This project allows users to **upload a dataset**, store it in **Neo4j**, and generate **Cypher queries dynamically using OpenAI**. Users can **ask questions** about their dataset, retrieve relevant insights, and visualize the results.

## 🛠 Features
✅ **Upload CSV, JSON, Excel, or Parquet files**  
✅ **Store data in a Neo4j graph database**  
✅ **Generate Cypher queries dynamically using OpenAI**  
✅ **Execute queries and fetch structured results**  
✅ **Visualize results using Plotly (if applicable)**  

---

## 📂 Project Structure
    📂 Neo4j-OpenAI-Query-Generator
    │
    ├── app.py                # Main Streamlit application
    ├── requirements.txt       # Python dependencies
    ├── README.md             # Project documentation
    └── .env/                # Environment variables for API keys (Not uploaded to GitHub)


## 🛠 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/Neo4j-OpenAI-Query-Generator.git
cd Neo4j-OpenAI-Query-Generator
```
### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
### 3️⃣ Set Up Environment Variables
Create a .env file and add your API keys:

```ini
OPENAI_API_KEY=your_openai_key
NEO4J_URI=neo4j+s://your-database.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

## 🚀 Running the Application
```bash
streamlit run app.py
```
This will open a Streamlit web application in your browser.

---

## 🎯 How It Works

### **📂 1. Upload Your Data**
- The app supports **CSV, JSON, Excel, and Parquet files**.
- The uploaded file is stored in **Neo4j as Entity nodes**.

### **🔍 2. Ask Questions About the Data**
- Enter a **natural language query**.
- **OpenAI converts** it into a **Cypher query**.
- The **Cypher query is executed** in Neo4j.

### **📊 3. View Results & Visualization**
- **Results are formatted** into a readable response.
- If applicable, a **Plotly bar chart is generated**.

---

## 🛠 Technologies Used
- **Streamlit** - Frontend UI  
- **Neo4j** - Graph database  
- **OpenAI GPT-4** - Query generation  
- **Pandas** - Data manipulation  
- **Plotly** - Data visualization  

---

## 📌 Example Usage

### ✅ **Uploading a Dataset**
1. Click on **Upload File**.
2. Select a **CSV, JSON, Excel, or Parquet file**.
3. Click **"Store Data in Neo4j"**.

### ✅ **Querying the Data**
**Example Question:**
> "Find the top 5 highest-rated reviews"

**Generated Cypher Query:**
```cypher
MATCH (r:Review)-[:RATING_GIVEN]->(rating:Rating)
RETURN r.title, r.rating
ORDER BY r.rating DESC
LIMIT 5;
```
### **Example Result:**
```yaml
Title: Best Laptop, Rating: 4.9
Title: Amazing Phone, Rating: 4.8
```
---

## 🔥 Future Improvements
- Support for large datasets with batch processing
- More visualization types (pie charts, line graphs)
- Advanced query tuning for better performance

## 🤝 Contributing
- Fork the repository
- Create a new branch (feature-branch)
- Commit your changes
- Push to GitHub and create a Pull Request

---

## 👨‍💻 Authors

| Aniketh Reddy Adireddy              | Rohan Sai Maragoni                 | Vamshi Kuruva                             |
|-------------------------------------|-----------------------------------|-------------------------------------------|
| [GitHub](https://github.com/Aniketh007)  | [GitHub](https://github.com/RohanSai22) | [GitHub](http://www.github.com/vamshikuruva) |
| [Email](mailto:anikethadireddy@gmail.com)  | [Email](mailto:maragonirohansai@gmail.com) | [LinkedIn](mailto:kuruvavamshi66@gmail.com) |
| [LinkedIn](https://www.linkedin.com/in/anikethreddy007/) | [LinkedIn](https://www.linkedin.com/in/rohan-sai-446a02228/) | [LinkedIn](https://www.linkedin.com/in/vamshikuruva/) |


