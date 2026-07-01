# 🎿 Ski Resort Analysis & Recommender

## 📌 Project Overview

This project combines **data analysis in Power BI** with an **interactive recommendation system built in Streamlit** to help users find the ski resort that best matches their travel preferences.

Using a dataset of more than **5,000 ski resorts worldwide**, the project analyzes factors such as:

- Skiable kilometers
- Resort size
- Snow reliability
- Freeride areas
- Snowparks
- Après-ski
- Family friendliness
- Gastronomy
- Lift infrastructure
- Price per kilometer
- Overall ratings

The final result is a data-driven recommendation tool that can be used by travel agencies or ski enthusiasts to discover the most suitable destinations.

---

## 📊 Power BI Dashboard

The Power BI report answers several business questions, including:

- Which countries offer the most skiable terrain?
- Which countries provide the best value for money?
- Which resorts are best suited for beginners or expert skiers?
- Where can the largest freeride areas be found?
- Is there a relationship between altitude and snow reliability?
- How are ski slopes distributed across the largest ski resorts?

### Dashboard Features

- Interactive filters
- KPI cards
- Geographic analysis
- Scatter plots
- Treemaps
- Comparative visualizations
- Ski resort profiling

---

## 🎿 Streamlit Recommendation App

The Streamlit application allows users to find ski resorts based on their preferences.

### Available Filters

- Continent
- Country
- Budget
- Minimum skiable kilometers
- Skier profile
  - Beginner
  - Intermediate
  - Expert
  - Freeride
- Travel type
  - General
  - Family
  - Party
  - Budget-friendly
  - Snowpark
  - Gastronomy

### Quality Filters

- Snow reliability
- Access and parking
- Signposting
- Cleanliness and hygiene
- Gastronomy
- Lifts and cable cars
- Snowparks
- Family friendliness
- Après-ski

### Features

- Personalized recommendations
- Resort comparison tool
- Smart filtering system
- Alternative suggestions when no exact match is found

---

## 🛠️ Technologies Used

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)

---

## 📂 Project Structure

```text
Ski Resort Analysis/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── eda.ipynb
│   ├── exploracion.ipynb
│   └── preprocesamiento.ipynb
│
├── app.py
├── requirements.txt
├── README.md
└── ski_resorts_dashboard.pbix
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/ski-resort-analysis.git
cd ski-resort-analysis
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```

---

## 🎯 Main Objective

To demonstrate how data analysis and recommendation systems can be combined to support decision-making in the tourism and travel industry.

---
