import allure

@allure.feature("Smoke")
@allure.story("Allure wiring")
def test_allure_smoke():
    with allure.step("Шаг 1: простая проверка"):
        assert 2 + 2 == 4
