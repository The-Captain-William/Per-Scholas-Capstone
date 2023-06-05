git # Per Scholas Data Engineering Bootcamp Capstone Project 
<br><br>

👉🏻 For Current and Future Update plans, click [here](#further-considerations-and-future-updates) <br>

## Introduction:


This Capstone Project is the culmination of my 17-week long Data Engineering bootcamp at Per Scholas, graciously powered by TEKSystems. 

It highlights many of the skills and technologies I've known previously and have managed to sharpen, as well as new skills and technologies I've learned along the way. 

### The Data Set & Workflow:
---
The Data-set is generated data representing that of a bank. <br>
The data consists of several large .JSON Files, and an API endpoint. <br> 
The data represents customer information, branch information, transaction history, as well as data pertaining to individuals applying for bank loans.

<div align="center">
<img src="https://raw.githubusercontent.com/The-Captain-William/Per-Scholas-Capstone/main/images/capstone_workflow_process.jpg" width=720px>
</div>
  
### The Project Components:
---
The capstone is divided into several components: 

<br><br>

<div align="center">
<table>
<th colspan="3"> <h2>Components</h2> </th>

  <tr>  <!-- ETL COLS -->
    <td>
    <h3>ETL </h3>
    </td>
    <td>
    <h3>Front End Interface</h3>
    </td>
    <td>
    <h3>Data Visualization</h3>
    </td>
  </tr>
  
<tr>
  <td>
  <p><a href='https://github.com/The-Captain-William/Per-Scholas-Capstone/blob/main/main/ETL/ETL_Part_1_building_the_database.ipynb'>Part One:</a><br>Building a SQL Database remotely with mysql.connector</p>
  <br>
  <p>
  <a href='https://github.com/The-Captain-William/Per-Scholas-Capstone/blob/main/main/ETL/ETL_Part_2_The_ETL_Process.ipynb'>Part Two:</a><br>My Entire ETL Workflow, including a few tips and tricks
  </p>
  </td>

<td>
<a href='https://raw.githubusercontent.com/The-Captain-William/Per-Scholas-Capstone/development/images/wip_sql_portal.png'>WIP Front-End User Portal</a>
</td>

</tr>
  
</table>
</div>

<br>

### ETL
---
**Outline:** <br>
An End-to-End ETL Pipeline was built with the purpose of Extracting data from the large JSON dataset and the API endpoint, Transforming the data appropriately, and Loading the data into a SQL database
<br>

**Technologies Used:** <br>
Languages: `Python` `SQL` `Batch`<br>
Major Python Libraries: `pyspark.sql` `mysql.connector` `requests` `pandas` `numpy` `dearpygui`

<br><br>
### Front-End Interface
---
**Outline:** <br>
A User-Friendly Front-End Interface I'm calling the *Data Explorer* is being built to interact with sql servers.
Using pyspark.sql and mysql.connector, a front end user can view and modify the contents of a SQL Database. 
The goal is to be able to have two forms of interaction, direct SQL code and abstracted-away SQL queries using nodes with the 
<a href='https://github.com/hoffstadt/DearPyGui'>DearPyGui</a> library. The user will be able to query, modify, and create graphs and visualizations directly from the Data Explorer. Could be very useful for datamarts.
<br>
<img src='https://raw.githubusercontent.com/The-Captain-William/Per-Scholas-Capstone/development/images/wip_sql_portal.png'>
<br>

**Technologies Used:**<br>
Languages: `Python` `SQL` <br>
Major Python Libraries: `pyspark.sql` `mysql.connector` `DearPyGui`
<br>

<br><br>
### Data Visualization
---
**Outline:**<br>
Data loaded onto the SQL database was queried through pyspark.sql and manipulated through pyspark.sql and Pandas to create datasets used for data visualization using matplotlib. 
<br>

**Technologies Used:**<br>
Languages: `Python` <br>
Major Python Libraries: `pandas` `matplotlib`
<br>

<br><br>
## Further Considerations and Future Updates
While I satisfied all of the requirements to land a perfect score on my capstone project grade, I want to take the liberty of really fleshing out this project and updating it to make it the best it can possibly be. 

