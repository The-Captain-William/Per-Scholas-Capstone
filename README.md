# Per Scholas Data Engineering Bootcamp Capstone Project 
<br><br>

👉🏻 For Current and Future Update plans, click [here](#further-considerations-and-future-updates)
👉🏻 For a Roadmap on what I'm currently working on, click [here](Roadmap.md)

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
Languages: `Python` `SQL` <br>
Major Python Libraries: `pyspark.sql` `mysql.connector` `requests` `pandas` `numpy`

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

- I've been experimenting with ETL techniques and plan on cleaning up the ETL jupyter notebook.
- The Terminal Application functionally *works* but  it definitely needs to be refactored into cleaner code. Its just a proof of concept for now.
- I plan on fleshing out and adding much more aesthetically pleasing graphs with matplotlib/seaborn and I'm also experimenting with tableau visualizations, which I will eventually link to the repo.

| Satus  | Meaning | 
| ------ | --------|
| 🛠     | In-Progress|
|↗       | Up-Next     |

This is just a birds-eye view. For a more granular look into progress check out my [Roadmap](Roadmap.md)

ETL
- [X] ✅ Create the SQL database through mysql.connector instead of pyspark.sql, allowing for more precise data types 
- [X] ✅ Rewrite all jupyter notebooks code, making  the pyspark.sql ETL process easier to read and more efficient 
- [ ] Copy MariaDB SQL database to a SQLite serverless database so users can view the finished product and interact with the front-ends with less work
- [ ] Compare the speeds of running pyspark.sql locally (using a single node) for the full ETL process with running pandas and discuss the appropriate use of each tool
- [ ] introduce the <a href="https://github.com/pola-rs/polars">Polars</a> library and further discuss speeds

Front-End

- [ ] GUI 
  - [ ] 🛠 Make a desktop GUI application that can interact with the server and produce graphs based on user input
    - [ ] Compile to .EXE
  - [ ] Consider building a web-app to emulate the same functionality 

Data Visualization
- [ ] Introduce extended graphing functionality and the ability to save rendered graphs created from the GUI
- [ ] Introduce a few Tableau graphs with Tableau Public


Documentation and Packaging
- [ ] Update README with todo tasks
- [ ] Include documentation for each component on a seperate markdown file
  - [ ] Update README to link included documentation
- [ ] Clean up all documentation
