import dearpygui.dearpygui as dpg

def add_checkbox_dropdown(limit: int | bool, choices: list, label: str =None, **kwargs):  # TODO make if False then skip limit
    with dpg.child_window(label="Dropdown Selection menu", **kwargs):
        limit = limit
        activated_list = []
        capture_ids = []


        def limit_checks(sender, app_data):



            def check_values(app_data: str | int, activated_list: list, limit: int):

                if app_data in activated_list:
                    activated_list.remove(app_data)
                elif app_data not in activated_list and len(activated_list) < limit:  # has to be less than b/c 2 < 3, then add 1, then 3 !< 3 : # NOTE can optimize w/ -= and += but kinda buggy rn
                #elif app_data not in activated_list and limit != 0:    
                    activated_list.append(app_data)

                return len(activated_list) == limit



                
            response = check_values(app_data=app_data, activated_list=activated_list, limit=limit)  # added kwarg style so I dont get confused


            if response == True:
                filter_id_children = dpg.get_item_children('filter_id')
                for child in filter_id_children[1]:  # dict
                    child = dpg.get_item_children(child)  # dict of dict
                    if child[1][1] not in activated_list:
                        capture_ids.append(child[1])  # list in dict
                        dpg.configure_item(child[1][1], enabled=False)  # checkbox
                        dpg.configure_item(child[1][0], color=(255, 0, 0))  # text, red
            


            elif response == False:
                for id in capture_ids:
                    dpg.configure_item(id[0], color=(255, 255, 255))  # text, white
                    dpg.configure_item(id[1], enabled=True)  # re-enable checkboxes



        with dpg.item_handler_registry(tag='checkbox_handler')as handler:
            dpg.add_item_activated_handler(callback=limit_checks)

        dpg.add_input_text(label='Filter', callback=lambda sender, app_data: dpg.set_value('filter_id', app_data), width=150)  # real time # remember app_data sends info captured 
        with dpg.child_window(height=200, width=200, tag='window_1', autosize_y=True):  # child window, THEN filter set
                with dpg.filter_set(tag="filter_id"):  
                    #test_list = list('ayeee lets get this bread')
                    # test_list_text_chechbox_id = []
                    for selection in choices:
                        # test_list_text_chechbox_id.clear()
                        dpg.add_group(parent='filter_id', horizontal=True, filter_key=selection)  # this might break if you have identical names..but you prob won't have identical names.
                        dpg.add_text(default_value=selection, parent=dpg.last_container())
                        dpg.add_checkbox(parent=dpg.last_container(), user_data=dpg.get_value(dpg.last_item()))  # sender, appdata, user_data
                        dpg.bind_item_handler_registry(dpg.last_item(), 'checkbox_handler')
                    
                    filter_id_children = dpg.get_item_children('filter_id')
                    for child in filter_id_children[1]:
                        child = dpg.get_item_children(child)
                        print(child[1])