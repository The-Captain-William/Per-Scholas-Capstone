import dearpygui.dearpygui as dpg
import mysql.connector as MariaDB
from mysql.connector.pooling import PooledMySQLConnection
from os import getenv
MariaDB.pooling.MySQLConnectionPool
from mysql.connector.cursor import MySQLCursor

# test_con = ConnectionHandler(pool_name='TestPool', database='db_capstone', user=getenv('DB_USER'), password=getenv('DB_PASSWORD'), host='localhost')

# cnx_1 = test_con.get_connection()

# cnx_cur = cnx_1.cursor()

# cnx_cur.execute("""
# SELECT DISTINCT(cust_state)
# FROM cdw_sapp_customer
# ORDER BY 1;
# """)

# for _ in cnx_cur:
#     print(_)


# class ConnectionHandler:
#     # explicitly define connection pool to instantiate multiple connections
#     # mothership
#     def __init__(self,
#                  pool_name: Optional[str] = None,
#                  database: Optional[str] = None,
#                  user: Optional[str] = None,
#                  password: Optional[str] = None,
#                  host: str = 'localhost'):
#         self.__internal_connection = MariaDB.pooling.MySQLConnectionPool(pool_name)



class ConnectionHandler:
    # explicitly define connection pool to instantiate multiple connections
    # mothership
    def __init__(self, connection: MariaDB.pooling.MySQLConnectionPool):
        """
        Wraps around a Mysql.Connector Connection pool. \n
        Example: 
            connection = ConnectionHandler( \n
            MariaDB.pooling.MySQLConnectionPool( \n
            pool_name = 'test', \n
            host='localhost',  \n
            user=getenv('DB_USER'), \n
            password=getenv('DB_PASSWORD'), \n
            database='db_capstone'  # db optional \n
            ) \n
        ) \n

        """
        self.__pool = connection
        self.__connections = {}
        self.__cursors = {}
        self.returns = {}

    # assign single connector from the internal connection 
    # connectionhandler.connection1 = connect()
    # single ship 
    # one connection per interface
    def create_connection(self, connection_name: str):
        """
        Establish a connection manually. 
        Technically not needed, you can jump right into ConnectionHandler.cur('connection_name')
        and a connection will be made for you if none exist.
        """
        self.__connections[connection_name] = self.__pool.get_connection()

        
    def cur(self, connection_name: str):
        """
        Establish a cursor with corresponding connection name.
        """
        try:
            if type(self.__connections[connection_name]) is PooledMySQLConnection:
                self.__cursors[connection_name] = self.__connections[connection_name].cursor()
                
        except KeyError:
            self.create_connection(connection_name=connection_name)
            self.cur(connection_name)


    def cur_execute(self, connection_name: str, connection_prompt: str, save: bool = True):
        """
        Executing a cursor with save default on true will allow you to access stored data from the 
        dictionary at a later time. 
        Example: 
            Set up:
                query = 'select * from table' \n
                connection = ConnectionHandler() \n
                connection.cursor('tomato') \n
                connection.execute('tomato', query) \n

            Access stored data:
                results = connection.return['tomato'][query]
        """

        try:
            self.__cursors[connection_name].execute(connection_prompt)
            if save == True:
                self.returns[connection_name] = {connection_prompt: [row for row in self.__cursors[connection_name]]}
            elif save == False:
                return [row for row in self.__cursors[connection_name]]


        except KeyError as e:
            print(f'Error, Cusor Not Found. {e}')


    def dict(self, connection_name: str = None, query: str = None):
        """
        Dictionary prints the names of the connections and cursors,
        as well as all of the stored queries and values. 
         
        To filter, choose connection name and/or query. 
        
        Choosing connection name will yield all queries and saved data
        for that particular connection.

        Choosing query and connection name will yield the connection name,
        and the saved data attached to that query.
        
        """ 
        print(self.__connections, self.__cursors)
        if connection_name is None:
            for key in self.returns.keys():
                for subkey in self.returns[key].keys():
                    print(subkey)
                    internal_list = self.returns[key][subkey]
                    for item in internal_list:
                        print(item)
        elif connection_name is not None and query is None:
            dictionary = self.returns[connection_name]
            for query_ in dictionary.keys():
                print(query_)
                for row in dictionary[query_]:
                    print(row)
        elif connection_name and query is not None:
            dictionary = self.returns[connection_name][query]
            print(query)
            for row in dictionary:
                print(row)





query = """
SELECT * 
FROM cdw_sapp_customer
LIMIT 10;
"""

query_2 = """
SELECT * 
FROM cdw_sapp_customer
LIMIT 2;
"""


connection = ConnectionHandler(
    MariaDB.pooling.MySQLConnectionPool(
    pool_name = 'test',
    host='localhost',  
    user=getenv('DB_USER'),
    password=getenv('DB_PASSWORD'),
    database='db_capstone'  # db optional
    )
)

# connection.create_connection('tomato')
connection.cur('tomato')
connection.cur_execute('tomato', query)
connection.cur_execute('tomato', query_2)


connection.dict('tomato')




# test = connection.cur_execute('tomato', query_2, save=False)

# print(test)

#server_connection.connection_1


####################
# server_connection = MariaDB.pooling.MySQLConnectionPool(
#     pool_name = 'test',
#     host='localhost',  
#     user=getenv('DB_USER'),
#     password=getenv('DB_PASSWORD'),
#     database='db_capstone'  # db optional
#     )


# cnx_cur = server_connection.get_connection()
# cnx_cur2 = server_connection.get_connection()

# cnx_cur_c = cnx_cur.cursor()
# cnx_cur2_c = cnx_cur2.cursor()


# cnx_cur_c.execute("""
# SELECT DISTINCT(cust_state)
# FROM cdw_sapp_customer
# ORDER BY 1;
# """)

# cnx_cur2_c.execute("""
# SELECT * 
# FROM cdw_sapp_customer
# LIMIT 10;
# """)

# for _ in cnx_cur_c:
#     print(_)

# for _ in cnx_cur2_c:
#     print(_)
############################

