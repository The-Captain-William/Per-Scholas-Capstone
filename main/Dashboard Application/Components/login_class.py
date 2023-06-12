import dearpygui.dearpygui as dpg
from types import FunctionType
from Components.generic_container import GenericContainerContext


class Login(GenericContainerContext):
    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)

    def grab_credentials(self):
        self.login_user = dpg.get_value(self._login_user)
        self.login_password = dpg.get_value(self._login_password)
        self.login_address = dpg.get_value(self._login_address)
        
    # def set_credentials(self, db_user: str, db_login: str, db_password:str):
    #     dpg.configure_item(self._login_user, default_value=db_user)
    #     dpg.configure_item(self._login_password, default_value=db_login)
    #     dpg.configure_item(self._login_address, default_value=db_password)

    
    def window(self, external_callback: FunctionType, default_login: str ='root', default_pass: str ='', default_address: str ='localhost', ):
        with dpg.menu(label='Login Information', tag=self.tag):
            self._login_user = dpg.add_input_text(label='Server Login Name', default_value=default_login, tag='user_box')
            self._login_password = dpg.add_input_text(label='Server Password', password=True, default_value=default_pass, tag='pw_box')
            self._login_address = dpg.add_input_text(label='Host', default_value=default_address, tag='host_box' )
            with dpg.group(horizontal=True):
                dpg.add_button(label='Login', callback=external_callback, user_data=self.tag, tag='login-confirm')
                self.login_response_tag = 'login-confirmation'
                dpg.add_text(tag=self.login_response_tag)

    # @property
    # def login_user(self):
    #     return self._login_user
    
    # @property
    # def login_password(self):
    #     return self._login_password

    # @property
    # def login_address(self):
    #     return self._login_address

    def toggle(self):
        return super().toggle()

    def confirm_login(self, response):
        if response is True:
            response = 'Login Succesful!'
        else:
            response = ''
        dpg.configure_item(self.login_response_tag, default_value=response)