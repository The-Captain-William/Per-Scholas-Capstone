import dearpygui.dearpygui as dpg


class GenericContainerContext:
    def __init__(self, container_tag: str, *args, **kwargs):
            print(kwargs)
            self.kwargs = kwargs
            self.args = args
            self.list = []
            self.tag = container_tag

    def display(self):
        pass

    def show(self):
        state = dpg.get_item_state(self.tag)['visible']  # get item state returns bool
        dpg.configure_item(self.tag, show=not state)  # negate bool


class Login(GenericContainerContext):
    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)

    def display(self):
        with dpg.window(label='test', tag=self.tag):
            pass

    def show(self):
        return super().show()
    
    