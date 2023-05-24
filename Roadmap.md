### GUI Stable Release 
- [ ] GUI Front-End
  - [ ] Consider making a desktop GUI application with ~~custimTkinter~~ dearpygui 
    - [ ] Going to need to have some method of automatically updating 'last_updated' columns
    - [ ] Compile to .EXE




 - [ ] SERVER INPUT -> ESTABLISH CONNECTION 
	 - [x] user id ✅ 2023-03-21
	 - [x] password ✅ 2023-03-21
	 - [x] port ✅ 2023-03-21
	 - [ ] w/e else we need
	 - [ ] save state to encrypted .txt or something
	 - [x] Make the password box an actual password box ✅ 2023-03-23

- [ ] CONFIRM CONNECTION ESTABLISHED
	- [ ] Some kind of cool live display
	- [x] show available databases ✅ 2023-03-21
		- [x] make clickable ✅ 2023-03-21
		- [x] add clickable functionality, USE DB ✅ 2023-03-23
		- [ ] make a nicer looking UI with select gui and name of db

- [ ] COLLECT TABLES FROM DB
	- [x] show table names ✅ 2023-03-23
	- [ ] show column names, datatypes



- [ ] BASIC QUERY 
	- [x] SQL select box ✅ 2023-03-23
	- [ ] run on key-press
	- [ ] working tab


- [ ] CLEANER REUSABLE FUNCTIONS 
	- [ ] update current database name in browser for all -> creare handler probably `1`



### Web-App Stable Release
  - [ ] Consider building a web-app to emulate the same functionality as the GUI


Data Visualization
- [ ] Redo matplot lib graphs to be more aesthetically pleasing, and more useful
- [ ] Introduce a few Tableau graphs with Tableau Public


Documentation and Packaging
- [ ] Update README with todo tasks
- [ ] Include documentation for each component on a seperate markdown file
  - [ ] Update README to link included documentation
- [ ] Refactor code to encapsulate everything together, perhaps using a an __Init__.py file or something 
- [ ] Clean up ETL and possibly remove pandas and / or bring those functions in via a seperate py  file
