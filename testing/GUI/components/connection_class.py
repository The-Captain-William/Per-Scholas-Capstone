import dearpygui.dearpygui as dpg
import mysql.connector as MariaDB
from mysql.connector.pooling import PooledMySQLConnection
MariaDB.pooling.MySQLConnectionPool
from typing import Optional

class ConnectionHandler(MariaDB.pooling.MySQLConnectionPool):
    # explicitly define connection pool to instantiate multiple connections
    # mothership

    def __init__(self, pool_name: Optional[str] = None, pool_size: int = 5, pool_reset_session: bool = True,
                 host='localhost', user: str = None, password: str = None, database: Optional[str] = None):        
        super().__init__(pool_name=pool_name, pool_size=pool_size, pool_reset_session=pool_reset_session, host=host, user=user, password=password, database=database)
        """
        Wraps around a Mysql.Connector Connection pool. \n
        Example: 
            connection = ConnectionHandler( \n
            pool_name = 'test', \n
            host='localhost',  \n
            user=getenv('DB_USER'), \n
            password=getenv('DB_PASSWORD'), \n
            database='db_capstone'  # db optional \n
            ) \n


        """

        #kwargs = kwargs.update({'host':host, 'user':user, 'password':password, 'database':database,
                                #'pool_name':pool_name, 'pool_size':pool_size, 'pool_reset_session':pool_reset_session})

        #self.__pool = self
        self.__connections = {}
        self.__cursors = {}
        self.__returns = {}












    # assign single connector from the internal connection 
    # connectionhandler.connection1 = connect()
    # single ship 
    # one connection per interface

    def __getitem__(self, connection_name):  # way to access item via dict or iteration
        return self.__returns[connection_name]

    def create_connection(self, connection_name: str):
        """
        Establish a connection manually. 
        Technically not needed, you can jump right into `ConnectionHandler.cur('connection_name')`
        and a connection will be made for you if none exist.
        """
        self.__connections[connection_name] = self.get_connection()

        
    def cur(self, connection_name: str):
        """
        Establish a cursor with corresponding connection name.
        """
        try:
            if type(self.__connections[connection_name]) is PooledMySQLConnection:
                self.__cursors[connection_name] = self.__connections[connection_name].cursor()
                self.__returns[connection_name] = {}
                
        except KeyError:
            self.create_connection(connection_name=connection_name)
            self.cur(connection_name)


    def cur_execute(self, connection_name: str, connection_prompt: str, save: bool = True):
        """
        Executing a cursor with save default on true will allow you to access stored data from the 
        dictionary at a later time, or any time you want.

        Execting a cursor with save default on false will allow you to access data only once, and then
        the data is wiped.

        Example: 
            Set up:
                `query = 'select * from table'` \n
                `connection = ConnectionHandler()` \n
                `connection.cursor('tomato')` \n
                `connection.execute('tomato', query)` \n

            Save is True:
                Access stored data:
                    `results = connection['tomato'][query]` \n
                    can be accessed any time 
            
            Save is False: 
                Access data:
                    `results = connection.execute('tomato', query)`
                     must be stored in results or another variable,
                     or it's lost forever.
                     can be useful for functions.

        """
        # { 'connection': {query: [results]}, {query2 : [results]},
        # {'connection2}
        # }

        try:
            self.__cursors[connection_name].execute(connection_prompt)
            if save == True:
                # self.__returns[connection_name] = {connection_prompt: [row for row in self.__cursors[connection_name]]}
                self.__returns[connection_name].update({connection_prompt: [row for row in self.__cursors[connection_name]]})


            
            elif save == False:
                return [row for row in self.__cursors[connection_name]]


        except KeyError as e:
            print(f'Error, Cusor Not Found. {e}')
    
    def pop(self, connection_name: str = None, query: str = None, all: bool = False):
        """
        You can delete the saved query of a connection with 
        `connection.pop('tomato', query)`

        You can delete all queries for a given connection with
        `connection.pop('tomato')`

        You can delete all queries for all connections with
        `connection.pop(all=True)`
        
        """
        if connection_name is not None and query is not None:
            del self.__returns[connection_name][query]
        
        elif connection_name is not None:
            del self.__returns[connection_name]

        elif all is True:
            self.__returns.clear()


    def show(self, connection_name: str = None, query: str = None):
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
            for key in self.__returns.keys():
                for subkey in self.__returns[key].keys():
                    print(subkey)
                    internal_list = self.__returns[key][subkey]
                    for item in internal_list:
                        print(item)
        elif connection_name is not None and query is None:
            dictionary = self.__returns[connection_name]
            for query_ in dictionary.keys():
                print(query_)
                for row in dictionary[query_]:
                    print(row)
        elif connection_name and query is not None:
            dictionary = self.__returns[connection_name][query]
            print(query)
            for row in dictionary:
                print(row)
    
    def close_connection(self, connection_name: str = None):
        """
        Enter the name of the connection to close the connection,
        or run connection.close_connection() without arguments
        to close all connections.
        """
        if connection_name is None:

            for connection in self.__connections.keys():
                self.__connections[connection].close()
                print(f"Closed {connection} Successfully")
                print(f"Closed all Connections in {self.__class__.__name__} sucessfully")


        elif connection_name is not None:
            try:
                self.__connections[connection_name].close()
                print(f"Closed {connection_name} succesfully")
            except KeyError:
                print(f"Connection Name: {connection_name} not found")






if __name__ =='__main__':
    # Examples for Inquiring Minds:

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

    from os import getenv
    # connection = ConnectionHandler(
    #     MariaDB.pooling.MySQLConnectionPool(
    #     pool_name = 'test',
    #     host='localhost',  
    #     user=getenv('DB_USER'),
    #     password=getenv('DB_PASSWORD'),
    #     database='db_capstone'  # db optional
    #     )
    # )


    connection = ConnectionHandler(
    pool_name ='test',
    pool_size=5, 
    host='localhost',  
    user=getenv('DB_USER'),
    password=getenv('DB_PASSWORD'),
    database='db_capstone'  # db optional
    )

    connection.create_connection('tomato')
    connection.cur('tomato')
    connection.cur_execute('tomato', query)
    connection.cur_execute('tomato', query_2)
    
    connection.show('tomato')

    connection.pop('tomato', query)
    connection.show('tomato')

    connection.pop(all=True)

    connection.close_connection()
