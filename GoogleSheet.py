import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Product import Product


class GoogleSheetService:
    tg_id = None
    name = None
    phone = None
    address = None
    add_inf = None
    orders = None
    delivery_date = None
    order_date = None

    def get_products_list_apiece(self):

        google_api = gspread.service_account(filename='nurdas-405909-6429504eed2c.json')
        products_sheet = google_api.open("Заказы Нурдас").worksheet('Продукция (поштучно)')
        products = []
        products_rows = products_sheet.get_all_values()

        for product_row in products_rows[1:]:
            product = Product(product_row[0], product_row[1], product_row[2], product_row[3])
            products.append(product)

        return products

    def get_products_list_packing(self):

        google_api = gspread.service_account(filename='nurdas-405909-6429504eed2c.json')
        products_sheet = google_api.open("Заказы Нурдас").worksheet('Продукция (упаковки)')
        products_rows = products_sheet.get_all_values()

        products = []
        for product_row in products_rows[1:]:
            product = Product(product_row[0], product_row[1], product_row[2], product_row[3])
            products.append(product)

        return products

    def write_order(self, tg_id, name, phone, address, add_inf, orders, delivery_date, order_date):
        # Подключение к таблице Google Sheets
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name('nurdas-405909-6429504eed2c.json', scope)
        client = gspread.authorize(credentials)

        # Открытие таблицы по ее названию
        sheet = client.open("Заказы Нурдас").worksheet('Заказы')

        # Получение последней заполненной строки
        row = len(sheet.get_all_values()) + 1
        self.tg_id = tg_id
        self.name = name
        self.phone = phone
        self.address = address
        self.add_inf = add_inf
        self.orders = orders
        self.delivery_date = delivery_date
        self.order_date = order_date
        # Добавление данных в следующую строку
        data = [self.tg_id, self.name, self.phone, self.address, self.add_inf, self.orders, self.delivery_date, self.order_date]
        sheet.insert_row(data, row)

