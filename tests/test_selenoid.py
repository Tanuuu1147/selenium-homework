def test_open_example(driver):
    driver.get("https://example.com")
    assert "Example" in driver.title
