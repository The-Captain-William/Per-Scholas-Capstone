import dearpygui.dearpygui as dpg
from types import FunctionType
from typing import Optional
from ConnectionHandler.connection_class import ConnectionHandler
from mysql.connector import Error as DBError


class GenericContainerContext:
    def __init__(self, container_tag: str, *args, **kwargs):
            self.kwargs = kwargs
            self.args = args
            self.list = []
            self.tag = container_tag

    def setup(self, connection: ConnectionHandler):
        """
        Set up the window with a connection and display databases available.
        """
        self.connection = connection
        self.connection.create_connection(self.tag)
        self.connection.cur(self.tag)

    def _mouse_move_callback(self, sender, data):
        """
        Create an item handler registry
        attach the item handler underneath with this function

        Then use a bind item handler registry to bind the item 
        you want to be affected by the registry to the registry.
        
        Example:\n
        `with dpg.child_window() as customer_table_group:`
            `with dpg.item_handler_registry() as mouse_hover:`
                `dpg.add_item_hover_handler(callback=self.mouse_move_callback)`

            `dpg.bind_item_handler_registry(customer_table_group, mouse_hover)`        
        """
        if dpg.get_mouse_pos() != self.mouse_pos:
            self.mouse_pos = dpg.get_mouse_pos(local=False)
            print(self.mouse_pos)

    @staticmethod
    def _collect_items(list: list):
        """
        queries return as a list of tuples (x, y);
        this will parse tuples and grab the first item.
        Works well if you know your query returns a single column
        """
        return [item[0] for item in list]


    def _connection_error(self, e):
        with dpg.window(label='Error'):
            dpg.add_text(f"Error, {e}")
            dpg.add_button(label='close', callback= lambda: dpg.configure_item(dpg.last_container(), show=False))

    # dropdown filter
    def _create_dropdown_filter(self, collection: list, parent_window: str | int, callback: Optional[FunctionType] = None):
        """
        Will create a dropdown filter given a parent window, the parent window being the filter set.
        """
        for item in collection:
            dpg.add_selectable(label=item, callback=callback, parent=parent_window, filter_key=item, user_data=item)

    def toggle(self):
        """
        Displays the window on or off
        """
        state = dpg.get_item_state(self.tag)['visible']  # get item state returns dict, dict ['visible'] returns bool
        dpg.configure_item(self.tag, show=not state)  # negate bool




    def _window_query_results(self, 
        results: list, parent: str | int, 
        button_column_number: Optional[int] = None, 
        button_callback: Optional[FunctionType] = None):

        """
        Displays query results for a window, 
        Optional Button parameter
        """
        self.contents = results
        dpg.delete_item(parent, children_only=True)



        for column_name in results[0]: # initiate headers
            dpg.add_table_column(label=column_name, parent=parent, width_stretch=False)
        
        if button_column_number != None:
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 15)
                    dpg.add_theme_color(dpg.mvThemeCol_Button, [32, 160, 192])
                    


            

            for row in results[1:]:  # initiate results
                with dpg.table_row(parent=parent):
                    for index, value in enumerate(row):
                        if index == button_column_number:
                            button = dpg.add_button(label=value, width=40, user_data=value, callback=button_callback)
                            dpg.bind_item_theme(button, theme)

                        else:
                            dpg.add_text(value, wrap=300)
        
        else:
            for row in results[1:]:  # initiate results
                with dpg.table_row(parent=parent):
                    for value in row:
                            dpg.add_text(value, wrap=300)


    def configure_plot(self, plot_id: int | str, 
                        number_of_graphs: int = 1, 
                        x: list = None, 
                        y1:list = None, 
                        y2: list = None, 
                        y3: list = None,
                        zero_ymin: bool = False,
                        x_ticks: list = None):
        """
        Plot has to be configured in this order: 
        plot:
            x_axis
            y_axis
            ... (w/e else)
            graphs (graphs w.r.t y_axis)
        Max 3 graphs
        """
        # setup plot
        plot_children_list = dpg.get_item_children(plot_id)[1]
        x_axis = plot_children_list[0]
        y_axis = plot_children_list[1]
        graphs = dpg.get_item_children(y_axis)

        if x_ticks == None:
            pass
        else:
            dpg.set_axis_ticks(x_axis, x_ticks)
                

        for graph_index in range(number_of_graphs, number_of_graphs + 1):
            graph = graphs[graph_index][0]  # graph 1, 2, 3 etc
            # graphs is type dict
            # graphs[1], graphs[2], graphs[3] all valid keys
            # keys yield lists, only one item in each list, access w/ 0
            
            
            if graph_index == 1:
                yval = y1
            elif graph_index == 2:
                yval = y2
            elif graph_index == 3:
                yval = y3
            
            if zero_ymin == True:
                ymin = 0
            else:
                ymin = min(yval) * 0.99
                ymax = max(yval) * 1.099
            
            dpg.configure_item(graph, x=x, y=yval)
            dpg.set_axis_limits(y_axis, ymin=ymin, ymax=ymax)