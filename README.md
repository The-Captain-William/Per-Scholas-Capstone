# Per Scholas Data Engineering Bootcamp Capstone Project
---



## Introduction
---
This Capstone Project is the culmination of a 15-week long Data Engineering bootcamp at Per Scholas.


It’s divided into several sections:
1.	ETL
2.	Terminal Interface
3.	API Extraction
4.	Data Visualization

<br>

### ETL
---
Several .JSON files were Extracted, Transformed, and Loaded into a SQL Database with the pyspark.sql module.


### Terminal Interface
---
A User-Friendly Terminal Interface was build to abstract away SQL queries. 
Using pyspark.sql and mysql.connector, a front end user can view and modify the contents of a SQL Database.


### API to SQL
---
Using pyspark.sql and the requests module, contents of an API were loaded into a SQL database. 


### Data Visualization
---
Data loaded onto the SQL database was queried through pyspark.sql and manipulated through pyspark.sql and Pandas to create datasets used for data visualization using matplotlib. 



### Further Considerations and Future Updates
---

#### ETL 
I've been experimenting with ETL techniques and plan on cleaning up the ETL jupyter notebook.
<br>

#### Terminal Interface
The Terminal Application functionally *works* but needs to be refactored into cleaner code. Its just a proof of concept for now.

I plan on creating a more generic Terminal Application Plugin and Also converting the terminal to EXE. 
<br>

#### Data Visualization
I plan on fleshing out and adding graphs via matplotlib and also experimenting with tableu visualizations.
