# Singapore Job Market Intelligence Dashboard

## 1. Business Understanding

### Business Scenario

Many job seekers search for jobs by looking at individual job advertisements. However, this makes it difficult to understand the overall job market, such as which industries pay higher salaries, have stronger hiring demand, or attract more competition. Career advisors and workforce planners also need a broader view of the job market to support career planning and workforce decisions.

### Business Case

**Build a data product that provides insights into Singapore's job market using historical job postings.**

The purpose of this project is to transform raw job posting data into an interactive dashboard that helps users better understand Singapore's job market through data visualisation and filtering.

### Target Users

The dashboard is intended for:

- Job seekers exploring career opportunities
- Career advisors supporting job seekers
- Workforce planners monitoring hiring trends

By presenting salary, hiring demand and competition in an interactive dashboard, users can compare industries more easily and make better-informed decisions.

### Business Questions

The dashboard was designed to answer the following business questions:

1. Which industries offer the highest average salaries?
2. Which industries have the greatest hiring demand?
3. Which industries receive the most job applications?
4. Which industries are hardest to fill?
5. How has hiring changed over time?

---

## 2. Data Understanding

The project uses the **SGJobData** dataset containing more than **one million historical job postings** in Singapore.

The dataset includes information such as:

- Company name
- Job title
- Industry category
- Employment type
- Position level
- Salary range
- Years of experience required
- Number of vacancies
- Job applications
- Job views
- Posting dates
- Repost information
- Job status

This information provides enough detail to analyse salary levels, hiring demand, competition and hiring trends across different industries.

---

## 3. Data Preparation

More than one million job postings were cleaned and prepared through:

- Removing empty records with missing job information
- Removing duplicate postings
- Standardising company names by removing unnecessary suffixes (such as "PTE. LTD.") and fixing inconsistent formatting
- Cleaning job titles by removing extra spaces and using proper title case
- Converting columns to appropriate data types (dates, categories and text)
- Removing unrealistic salary records (very low salaries, unusually high salaries and abnormal salary ranges)
- Job postings requiring 30 years or more of experience were removed because they represented approximately the top 0.01% of the data and were considered unrealistic.
- Checked repost consistency
- Saving the cleaned dataset for dashboard development

These steps improved data quality and ensured reliable analysis.

---

## 4. Dashboard Development and Findings

The dashboard was developed using **Streamlit**, **Pandas** and **Plotly**. Users can filter job postings by salary, industry, employment type, position level, experience, posting period and job status. The dashboard updates automatically based on the selected filters.

The dashboard answers the five business questions through interactive charts showing:

- Average salary by industry
- Hiring demand based on total vacancies
- Number of job applications by industry
- Industries that required the most reposts
- Hiring trends over time

Users can also browse the filtered job postings in a searchable table.

### Key Business Findings

- **Legal, Risk Management** and **Banking & Finance** offer the highest average monthly salaries.
- Hiring demand remains strong across many industries, with consistent recruitment activity over time.
- Competition differs across industries, with some industries attracting far more applications than others.
- The dashboard allows users to interactively explore salary levels, hiring demand, competition and employment patterns to support better career and workforce decisions.

---

## Challenges and Learning

### Challenge

The SGJobData dataset contained several common data quality issues, including missing values, duplicate records, inconsistent text formatting, extra whitespace, and multiple category IDs stored within a single field. It also contained inconsistent salary values, incorrect data types, and inconsistent company names, all of which reduced the overall quality of the dataset. Considerable effort was required to clean and validate the data so that the analysis would be as accurate and reliable as possible for HR decision-making, salary benchmarking, and job matching.

Another challenge was deciding which insights to include in the dashboard. Since the dataset supports many different analyses and KPIs, it was important to prioritise the most meaningful ones so that the dashboard remained clear, focused, and easy to use.

### What We Learned

This project showed that data cleaning is one of the most important stages of the data analytics process. High-quality and consistent data leads to more accurate analysis and more reliable insights. The project also provided hands-on experience using Pandas for data cleaning and Streamlit to build an interactive dashboard that presents information in a clear and user-friendly way.