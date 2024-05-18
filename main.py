import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options


# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    order_taxi_button = (By.XPATH, '//*[contains(text(), "Pedir un taxi")]')
    comfort_tariff_button = (By.XPATH, '//*[contains(text(), "Comfort")]')
    telephone_number = (By.CLASS_NAME, "np-button")
    phone_input = (By.ID, 'phone')
    next_button = (By.XPATH, '//*[contains(text(), "Siguiente")]')
    code_field = (By.ID, 'code')
    code_confirmation_button = (By.XPATH, '//*[contains(text(), "Confirmar")]')
    payment_method = (By.CLASS_NAME, "pp-button")
    add_card = (By.XPATH, '//*[contains(text(), "Agregar tarjeta")]')
    card_number_field = (By.XPATH, '//*[@id="number"]')
    card_code_field = (By.NAME, 'code')
    add_button = (By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[2]/form/div[3]/button[1]')
    card_close_button = (By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[1]/button')
    message = (By.ID, 'comment')
    blanket_and_scarves_switch = (
    By.XPATH, '//*[@id="root"]/div/div[3]/div[3]/div[2]/div[2]/div[4]/div[2]/div[1]/div/div[2]/div')
    add_icecream = (By.XPATH,
                    '//*[@id="root"]/div/div[3]/div[3]/div[2]/div[2]/div[4]/div[2]/div[3]/div/div[2]/div[1]/div/div['
                    '2]/div/div[3]')
    order_a_taxi = (By.CLASS_NAME, "smart-button-wrapper")
    modal_opcional = (By.XPATH,'//*[contains(text(), "El conductor llegará en")]')
    def __init__(self, driver):
        self.driver = driver

    # Métodos de acciones en la página
    def set_from(self, from_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def click_order_taxi_button(self):
        self.driver.find_element(*self.order_taxi_button).click()

    def click_comfort_tariff_button(self):
        self.driver.find_element(*self.comfort_tariff_button).click()

    def click_phone_number_field(self):
        self.driver.find_element(*self.telephone_number).click()

    def fill_in_phone_number(self):
        self.driver.find_element(*self.phone_input).send_keys(data.phone_number)

    def click_next_button(self):
        self.driver.find_element(*self.next_button).click()

    def set_confirmation_code(self, code):
        self.driver.find_element(*self.code_field).send_keys(code)

    def click_code_confirmation_button(self):
        self.driver.find_element(*self.code_confirmation_button).click()

    def click_payment_method_field(self):
        self.driver.find_element(*self.payment_method).click()

    def click_add_card_button(self):
        self.driver.find_element(*self.add_card).click()

    def enter_card_number(self):
        self.driver.find_element(*self.card_number_field).send_keys(data.card_number)

    def enter_card_code(self):
        self.driver.find_element(*self.card_code_field).send_keys(data.card_code)

    def press_tab_key(self):
        self.driver.find_element(*self.card_code_field).send_keys(Keys.TAB)

    def click_add_button(self):
        self.driver.find_element(*self.add_button).click()

    def click_card_close_button(self):
        self.driver.find_element(*self.card_close_button).click()

    def enter_new_message(self):
        self.driver.find_element(*self.message).send_keys('Hola buen día')

    def click_blanket_and_scarves_switch(self):
        self.driver.find_element(*self.blanket_and_scarves_switch).click()

    def click_add_icecream(self):
        self.driver.find_element(*self.add_icecream).click()

    def click_order_a_taxi(self):
        self.driver.find_element(*self.order_a_taxi).click()

    def wait_opcional_modal(self):
        self.driver.find_element(*self.modal_opcional)


class TestUrbanRoutes:
    driver = None

    @classmethod
    def setup_class(cls):
        chrome_options = Options()
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)

    def test_set_route(self):
        # 1. Abrir Urban Routes en Chrome.
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)

        # 2. Establecer las direcciones de origen y destino.
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_from(address_from)
        routes_page.set_to(address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

        # 3. Seleccionar la tarifa "Comfort".
        routes_page.click_order_taxi_button()
        routes_page.click_comfort_tariff_button()

        # 4. Rellenar el número de teléfono.
        routes_page.click_phone_number_field()
        routes_page.fill_in_phone_number()
        routes_page.click_next_button()
        code = retrieve_phone_code(self.driver)
        routes_page.set_confirmation_code(code)
        routes_page.click_code_confirmation_button()

        # 5. Agregar tarjeta de crédito.
        routes_page.click_payment_method_field()
        routes_page.click_add_card_button()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(routes_page.card_number_field)
        ).send_keys(data.card_number)
        routes_page.enter_card_number()
        routes_page.enter_card_code()
        routes_page.press_tab_key()
        routes_page.click_add_button()
        routes_page.click_card_close_button()

        # 6. Escribir un mensaje para el controlador.
        routes_page.enter_new_message()

        # 7. Pedir manta y pañuelos.
        routes_page.click_blanket_and_scarves_switch()

        # 8. Pedir 2 helados.
        routes_page.click_add_icecream()
        routes_page.click_add_icecream()

        # 9. Buscar un taxi.
        routes_page.click_order_a_taxi()
        WebDriverWait(self.driver, 40).until(
            expected_conditions.visibility_of_element_located(routes_page.modal_opcional)
        )

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
