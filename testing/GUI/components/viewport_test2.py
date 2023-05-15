import dearpygui.dearpygui as dpg
from Components import *
from dearpygui.demo import show_demo
#from ConnectionHandler.connection_class import ConnectionHandler


# TODO:
# create date and buttons dropdown or find a way to fix date module
# more filtering based off of dates
# graphs


if __name__ == "__main__":
    try:
        from os import getenv
        db_user = getenv('DB_USER')
        db_password = getenv('DB_PASSWORD')
    except Exception:
        db_user = ''
        db_password = ''


connection = None

login_window = Login('login window')
query_window = QueryPortal('query window')
saap_window = SaapPortal('Saap Portal')
customer_window = CustomerPortal('Customer Portal')

def viewport_buttons(enabled: bool):
    pass


def event_handler():
    try:
        login_window.grab_credentials()
        
        global connection
        connection = ConnectionHandler(
                pool_name='DataExplorer',
                host=login_window.login_address,
                user=login_window.login_user,
                password=login_window.login_password,
                )
        login_window.confirm_login(True)

        query_window.setup(connection)
        saap_window.setup(connection)
        customer_window.setup(connection)
        

        dpg.configure_item(viewport_query_button, enabled=True)

    except DBError as e:
        with dpg.window(label='Error'):
            dpg.add_text(f"Error, {e}")
            dpg.add_button(label='close', callback= lambda: dpg.configure_item(dpg.last_container(), show=False))
            login_window.confirm_login(False)
            dpg.configure_item(viewport_query_button, enabled=False)


# dpg.bind_item_font(saap_window.piechart_report_group, font=inter_regular_15)



dpg.create_context()
dpg.setup_dearpygui()

dpg.create_viewport(title='Data Explorer', width=2000, height=1200)

dpg.show_style_editor()
dpg.show_item_registry()

with dpg.font_registry():
    inter_regular_18 = dpg.add_font('Font/Inter/Inter.ttf', 18)
    inter_regular_15 = dpg.add_font('Font/Inter/Inter.ttf', 15)



with dpg.viewport_menu_bar():
    login_window.window(default_login=db_user, default_pass=db_password, external_callback=event_handler)
    
    # package this
    viewport_query_button = dpg.add_button(label='Query Portal', callback=query_window.toggle)
    vieport_saap_button = dpg.add_button(label='Business Analytics Dashboard', callback=saap_window.toggle)
    viewport_customer_button = dpg.add_button(label='Customers Database', callback=customer_window.toggle)
    query_window.window()
    saap_window.window()
    customer_window.window()

#show_demo()



with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        # window bg
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 25), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (32, 32, 32), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (37, 37, 38), category=dpg.mvThemeCat_Core)
        
        # scrollbar
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (214, 214, 214), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (240, 240, 241), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (255, 255, 255), category=dpg.mvThemeCat_Core)
        
        # window bg
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (15, 15, 15), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (41, 41, 41), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (37, 37, 38), category=dpg.mvThemeCat_Core)

        # tabs
        dpg.add_theme_color(dpg.mvThemeCol_Tab, (51, 51, 55), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (221, 221, 221, 103), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, (88, 144, 165, 153), category=dpg.mvThemeCat_Core)

        # buttons
        dpg.add_theme_color(dpg.mvThemeCol_Button, (69, 73, 83), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (207, 207, 207, 103), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (230, 230, 230, 153), category=dpg.mvThemeCat_Core)

        # table
#        dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, (164, 192, 207, 11), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, (164, 192, 207, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, (164, 192, 207, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, (193, 195, 203, 61), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (45, 43, 43, 255), category=dpg.mvThemeCat_Core)


        # checkmark, radio
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (46, 225, 175, 232), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (191, 196, 199, 103), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (255, 255, 255, 153), category=dpg.mvThemeCat_Core)


        # plot global
        dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 0), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (0, 0, 0, 0), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_Line, (38, 255, 144, 255), category=dpg.mvThemeCat_Plots)


        # window styles
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 3, category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvListbox):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (46, 225, 175, 232), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Header, value=(0, 0, 0, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, value=(104, 255, 199, 232), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, value=(193, 255, 232, 232), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, value=(0, 0, 0, 255))






with dpg.theme() as analytics_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (32, 32, 0, 0), category=dpg.mvThemeCat_Core)
    
    with dpg.theme_component(dpg.mvPlot):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (0, 0, 0, 0), category=dpg.mvThemeCat_Plots)
    

with dpg.theme() as customer_analytics_theme:
    with dpg.theme_component(dpg.mvPlot):
        dpg.add_theme_color(dpg.mvPlotCol_Fill, (0, 255, 113, 255), category=dpg.mvThemeCat_Plots)


dpg.bind_font(inter_regular_18)
dpg.bind_item_font(saap_window.piechart_report_group, font=inter_regular_15)
dpg.bind_item_font(saap_window.state_transaction_by_type_group, font=inter_regular_15)
dpg.bind_item_font(saap_window.region_plot_group, font=inter_regular_15)



dpg.bind_theme(global_theme)


dpg.bind_item_theme(saap_window.region_plot_group, theme=analytics_theme)
dpg.bind_item_theme(saap_window.region_report_group, theme=analytics_theme)
dpg.bind_item_theme(saap_window.piechart_report_group, theme=analytics_theme)
dpg.bind_item_theme(saap_window.transaction_count_and_volume_group, theme=analytics_theme)
dpg.bind_item_theme(saap_window.transaction_by_state_group, theme=analytics_theme)
dpg.bind_item_theme(saap_window.big_graphs_group, theme=analytics_theme)
dpg.bind_item_theme(saap_window.company_plot_big_graphs_group, theme=analytics_theme)
dpg.bind_item_theme(saap_window.state_transaction_by_type_group, theme=analytics_theme)
dpg.bind_item_theme(saap_window.state_region_dropdown_group, theme=analytics_theme)

dpg.bind_item_theme(saap_window.big_graphs_group, theme=customer_analytics_theme)




dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()


def close(connection: ConnectionHandler):
    try:
        connection.close_connection()
    except AttributeError:
        pass




close(connection)
