class UserSession:

    current_order = None
    orders = []
    user_id = None
    name = None
    phone = None
    address = None
    add_inf = None
    delivery_date = None
    change_title = None
    change_product = False
    change_weight = False
    number_str_for_change = None

    def __init__(self, state):
        self.state = state

    def default_parameters(self):
        self.current_order = None
        self.orders = []
        self.user_id = None
        self.name = None
        self.phone = None
        self.address = None
        self.add_inf = None
        self.delivery_date = None
        self.change_title = None
        self.change_product = False
        self.change_weight = False
        self.number_str_for_change = None
