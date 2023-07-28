# ETL Pipeline with Apache PySpark and Front End Desktop Application

![Entire Process](./main/ETL%20Process/Jupyter%20Notebook/images/ETL%20Process.png)

<div>
<table>
  <tr>
    <td>
    <img src="https://github.com/The-Captain-William/Per-Scholas-Capstone/blob/main/Screenshot%202023-07-22%20143008.png?raw=true">
    </td>
    <td>
      <img src="https://github.com/The-Captain-William/Per-Scholas-Capstone/blob/main/Screenshot%202023-07-28%20192240.png?raw=true">
    </td>
  </tr>
  <tr>
    <td>
      <img src="https://github.com/The-Captain-William/Per-Scholas-Capstone/blob/main/Screenshot%202023-07-22%20143155.png?raw=true">
    </td>
    <td>
      <img src="https://github.com/The-Captain-William/Per-Scholas-Capstone/blob/main/Screenshot%202023-07-22%20143029.png?raw=true">
    </td>
  </tr>
</table>
</div>

<div>
  <a href="https://youtu.be/p48iFH-Ysb0">
    <img src="https://clipart.info/images/ccovers/1590430652red-youtube-logo-png-xl.png" width=100px alt="youtube link">  
    <p>Click to Watch the video!</p>
  </a>
</div>

This is a full-stack solution for a bank, from the cleaning of the data to the creation of a database to a custom-built Windows data analytics application.

The original main objective of this project was to develop an ETL (Extract, Transform, Load) pipeline using Apache PySpark and Jupyter Notebook. The pipeline extracts data from various JSON files and an API, performs necessary transformations, and loads the data into a local database. 

However, I went beyond the initial requirements and implemented several optimizations, hosted the database on Amazon AWS, and created a user-friendly data analytics dashboard.

To explore the project and download the data analytics dashboard, [please visit the project's release page](https://github.com/The-Captain-William/Per-Scholas-Capstone/releases/tag/v1.3). The database is live and accessible, and detailed instructions can be found in the provided link.

Please note that this README provides a summary of the project. For detailed information and code implementation, please refer to the respective sections and files in the repository.

Feel free to explore the project, and if you have any questions or feedback, please don't hesitate to reach out!

**Technologies Used:** <br>
Languages: `Python` `SQL` `Batch`<br>
Key Python Libraries: `pyspark.sql` `mysql.connector` `requests` `pandas` `numpy` `dearpygui` <br>
Database Hosting: `Amazon AWS RDS`


  
### Project Steps:
---

#### 1. Building the Database
- I designed a data warehouse as a relational database that contains 5 tables and 3 materialized views, employing correct data types.
- The database was built with MySQL.connector using appropriate datatypes.
- The database was then hosted using Amazon AWS services.
- [Click this link](https://github.com/The-Captain-William/Per-Scholas-Capstone/blob/main/main/ETL%20Process/Jupyter%20Notebook/ETL_Part_1_building_the_database.ipynb) to be taken to the Database Creation section of the repository. 

#### 2. Extracting, Transforming, and Loading the Data 
- The dataset used in this project consists of synthetic bank data, comprising several large JSON files and an API endpoint.
- The data encompasses customer information, branch details, transaction history, and loan application records.
- Using Jupyter Notebook and Apache Spark through PySpark, the data was Extracted, Transformed, and Loaded onto the Database.
- [Click this link](https://github.com/The-Captain-William/Per-Scholas-Capstone/blob/main/main/ETL%20Process/Jupyter%20Notebook/ETL_Part_2_The_ETL_Process.ipynb) to be taken to the ETL section of the repository.

#### 3. Building a Data Analytics Windows Desktop 
- I implemented Object-Oriented Principles (OOP) in Python for desktop app development, creating 6 classes with 4 inheriting from a base class and over 30 methods.
- I released the application as an executable (EXE), eliminating the need for Python dependencies or interpreter installation (of course, the source code is still available). The setup can be completed in as little as 5 minutes.
- Implemented a class object around the MySQLConnectionPool to facilitate seamless data flow between the app and the server.


### Optimizations:
---
- A lot of what the analytics dashboard pulls from are from complex materialized views on the database that I tested and optimized for faster querying. 
However, if I wanted to increase performance even more, I could have used numpy a little more liberally and swapped out the default Python arrays for numpy arrays.

- The queries are baked into the objects and therefore baked into the exe, but next time I'll be sure to keep the queries in stored procedures server side along with
the materialized views for even faster querying and to keep from having to recompile the exe if anything serverside were to ever change.

### Lessons Learned:
---
- I learned going into the project that the DearPyGui GUI framework is more script-based and not object-oriented based. 
This made it *extremely* complicated to try to develop a desktop app of this caliber and handle all the data coming in and going out, so I built my own objects
using components from the framework. Each distinct object is essentially a window in the application, and they are all loosely coupled, with a viewport holding them all together.
Some windows share similar functions, and those functions are all inherited from a base class. While I enjoyed using the framework, I will make sure to read documentation and code examples *thoroughly*
before attempting to use them for another project.

- I also built a way to capture and temporarily cache data coming in from the database using hash tables, which is the secret sauce of how I managed to make the customer data appear to be directly editable from the rows as they populate.

### Extras:
---
- For an example of how I created stored procedures and triggers in PostgreSQL in another project, click <a href='https://github.com/The-Captain-William/stored-procedures-and-triggers-psql'>here</a>




