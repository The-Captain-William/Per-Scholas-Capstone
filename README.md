# ETL Pipeline with Apache PySpark and Front End App with DearPyGui

This Capstone Project was made during a Data Engineering Bootcamp I attended at Per Scholas.

![Entire Process](./main/ETL%20Process/Jupyter%20Notebook/images/ETL%20Process.png)


This is a capstone project from my Data Engineering Bootcamp. <br>
I built a full-stack solution, from the cleaning of the data, to the creation of a database, to a custom-built Windows data analytics application.

The original main objective of this project was to develop an ETL (Extract, Transform, Load) pipeline using Apache PySpark and Jupyter Notebook. The pipeline extracts data from various JSON files and an API, performs necessary transformations, and loads the data into a local database. 

However, I went beyond the initial requirements and implemented several optimizations, hosted the database on Amazon AWS, and created a user-friendly data analytics dashboard.

To explore the project and download the data analytics dashboard, [please visit the project's release page](https://github.com/The-Captain-William/Per-Scholas-Capstone/releases/tag/v1.3). The database is live and accessible, and detailed instructions can be found in the provided link.

Please note that this README provides a summary of the project. For detailed information and code implementation, please refer to the respective sections and files in the repository.

Feel free to explore the project, and if you have any questions or feedback, please don't hesitate to reach out!
  
### Project Steps:
---

#### 1. Building the Database
- The database was built with Jupyter Notebook and MySQL.connector using appropriate datatypes.
- The database was then hosted using Amazon AWS services.
- [Click this link](https://github.com/The-Captain-William/Per-Scholas-Capstone/blob/main/main/ETL%20Process/Jupyter%20Notebook/ETL_Part_1_building_the_database.ipynb) to be taken to the Database Creation section of the repository. 

#### 2. Extracting, Transforming, and Loading the Data 
- Using Jupyter Notebook and Apache Spark through PySpark, the data was Extracted, Transformed (and cleaned) and Loaded onto the Database.
- [Click this link](https://github.com/The-Captain-William/Per-Scholas-Capstone/blob/main/main/ETL%20Process/Jupyter%20Notebook/ETL_Part_2_The_ETL_Process.ipynb) to be taken to the ETL section of the repository.

#### 3. Building a Data Analytics Windows Desktop 
- Developed a powerful data analytics application called Data Explorer, which can be downloaded and easily installed.
- The app was built using object-oriented principles, incorporating custom objects and comprehensive testing for edge cases.
- Implemented a class object around the MySQLConnectionPool to facilitate seamless data flow between the app and the server.

### The Data Set
---
- The dataset used in this project consists of synthetic bank data, comprising several large JSON files and an API endpoint.
- The data encompasses customer information, branch details, transaction history, and loan application records.


**Technologies Used:** <br>
Languages: `Python` `SQL` `Batch`<br>
Key Python Libraries: `pyspark.sql` `mysql.connector` `requests` `pandas` `numpy` `dearpygui` <br>
Database Hosting: `Amazon AWS RDS`



