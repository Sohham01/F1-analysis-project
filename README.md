# 🏎️ Formula 1 Analytics Hub

## Overview

Formula 1 Analytics Hub is an interactive data analytics dashboard built using Python and Streamlit. The project explores historical Formula 1 race data through data cleaning, exploratory analysis, visualization, and predictive modeling.

The dashboard allows users to analyze driver performance, constructor statistics, race weekends, championship standings, and machine learning predictions through an intuitive web interface.

---

## Features

### 📊 Overview Dashboard

* Historical Formula 1 statistics
* Global F1 circuit map
* Season progression analysis
* Driver and Constructor standings
* Championship trends

### 👨‍🏎️ Driver Analytics

* Driver profile lookup
* Career statistics
* Wins, podiums, poles, and points
* Head-to-head driver comparison
* Radar chart performance analysis

### 🏁 Constructor Analytics

* Constructor performance history
* Seasonal points progression
* Teammate battle analysis
* Qualifying comparisons
* Race performance comparisons

### 🔧 Race Weekend Analysis

* Official race classifications
* Lap pace analysis
* Pit stop analytics
* Grid vs Finish position analysis
* Race telemetry exploration

### 🤖 Predictive Analytics

Machine Learning model built using Linear Regression.

Features used:

* Starting Grid Position
* Driver Experience
* Recent Driver Form
* Team Championship Points

Evaluation Metrics:

* R² Score
* Mean Absolute Error (MAE)
* Root Mean Squared Error (RMSE)

---

## Technologies Used

### Programming Language

* Python

### Libraries

* Streamlit
* Pandas
* NumPy
* Plotly
* Scikit-Learn
* Matplotlib

### Data Science Techniques

* Data Cleaning
* Data Wrangling
* Exploratory Data Analysis (EDA)
* Feature Engineering
* Regression Modeling
* Interactive Visualization

---

## Project Structure

```text
PL2_Project/
│
├── Dashboard/
│   ├── app.py
│   ├── data_loader.py
│   ├── styles.css
│   │
│   └── Pages/
│       ├── 1_Overview.py
│       ├── 2_Drivers.py
│       ├── 3_Constructors.py
│       ├── 4_Race_Weekend.py
│       └── 5_Predictive_Analytics.py
│
├── Data/
│   ├── drivers.csv
│   ├── constructors.csv
│   ├── races.csv
│   ├── results.csv
│   └── ...
│
├── Notebooks/
│   ├── 1_data_cleaning.ipynb
│   ├── 2_analysis_visualization.ipynb
│   ├── 3_predictive_modeling.ipynb
│   └── Exploration.ipynb
│
├── requirements.txt
├── verify.py
├── README.md
└── .gitignore
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/F1-analysis-project.git
cd F1-analysis-project
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Dashboard

From the Dashboard directory:

```bash
streamlit run app.py
```

The dashboard will launch in your browser at:

```text
http://localhost:8501
```

---

## Dataset

Source:
Ergast Formula One Historical Database

Contains:

* Drivers
* Constructors
* Races
* Circuits
* Results
* Qualifying Data
* Pit Stops
* Driver Standings
* Constructor Standings

---

## Learning Outcomes

This project demonstrates:

* Data Collection and Preparation
* Data Cleaning and Transformation
* Interactive Dashboard Development
* Exploratory Data Analysis
* Statistical Analysis
* Machine Learning Implementation
* Data Visualization
* Software Project Organization

---

## Group Information

### Group No. 7

1. Apurv Singh (Roll no.-2025BSDSAI021)
2. Gaurav Singh (Roll no.-2025BSDSAI042)
3. Livaansh Choudhary (Roll no.-2025BSDSAI049)
4. Sohham Choudhary (Roll no.-2025BSDSAI077)
5. Yuvraj Rao Padala (Roll no.-2025BSDSAI086)

---

## License

This project is developed for academic purposes as part of a Data Analytics and Programming Laboratory course.
