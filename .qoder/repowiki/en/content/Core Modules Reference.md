# Core Modules Reference

<cite>
**Referenced Files in This Document**   
- [conftest.py](file://conftest.py)
- [utils/waits.py](file://utils/waits.py)
- [docker-compose.yml](file://docker-compose.yml)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Configuration and Test Fixtures](#configuration-and-test-fixtures)
3. [Custom Wait Utilities](#custom-wait-utilities)
4. [Docker-Based Test Environment](#docker-based-test-environment)
5. [Usage Examples](#usage-examples)
6. [Performance Implications and Best Practices](#performance-implications-and-best-practices)

## Introduction
This document provides a comprehensive reference for the foundational modules that power the automated test framework in the OpenCart testing suite. It details the core components responsible for test configuration, browser management, synchronization, and environment isolation. The analysis covers `conftest.py` for pytest fixtures, `utils/waits.py` for enhanced Selenium wait conditions, and `docker-compose.yml` for containerized test environments.

## Configuration and Test Fixtures

The `conftest.py` file serves as the central configuration hub for the pytest-based test framework, defining command-line options and reusable fixtures that manage test setup and teardown. These fixtures provide consistent access to the browser instance, base URLs, and administrative credentials across test cases.

### Command-Line Options
The `pytest_addoption` hook introduces configurable parameters:
- `--browser`: Specifies the browser to use (chrome, firefox, safari)
- `--base-url`: Sets the target OpenCart instance URL
- `--admin-path`: Defines the admin panel path
- `--admin-username` and `--admin-password`: Credentials for admin access
- `--headless`: Enables headless browser execution

### Key Fixtures

#### base_url
```python
@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url").rstrip("/")
```
- **Scope**: Session-level (shared across all tests)
- **Lifecycle**: Initialized once per test session, reused by all tests
- **Purpose**: Provides the root URL for the OpenCart application
- **Dependencies**: None

#### admin_path
```python
@pytest.fixture(scope="session")
def admin_path(request):
    path = request.config.getoption("--admin-path")
    return path if path.startswith("/") else "/" + path
```
- **Scope**: Session-level
- **Lifecycle**: Created once per session
- **Purpose**: Normalizes the admin path to ensure it starts with a slash
- **Dependencies**: Depends on `--admin-path` CLI option

#### admin_creds
```python
@pytest.fixture(scope="session")
def admin_creds(request):
    return {
        "user": request.config.getoption("--admin-username"),
        "password": request.config.getoption("--admin-password"),
    }
```
- **Scope**: Session-level
- **Lifecycle**: Initialized once per session
- **Purpose**: Encapsulates admin credentials, with fallback to environment variables
- **Dependencies**: Relies on `--admin-username` and `--admin-password` CLI options

#### browser
```python
@pytest.fixture
def browser(request):
    # Browser setup logic for Chrome, Firefox, Safari
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()
```
- **Scope**: Function-level (fresh instance per test)
- **Lifecycle**: Created before each test, destroyed after test completion
- **Purpose**: Manages WebDriver instance with configurable browser and headless mode
- **Dependencies**: Depends on `--browser` and `--headless` options
- **Configuration**: 
  - 30-second page load timeout
  - 2-second implicit wait
  - Window size set to 1280x900
  - Automatic driver cleanup via `yield`/`quit()`

#### wait
```python
@pytest.fixture
def wait(browser):
    return WebDriverWait(browser, 10)
```
- **Scope**: Function-level
- **Lifecycle**: Created per test function
- **Purpose**: Provides a WebDriverWait instance with 10-second timeout
- **Dependencies**: Directly depends on the `browser` fixture
- **Usage**: Enables explicit waits for element visibility, clickability, etc.

**Section sources**
- [conftest.py](file://conftest.py#L0-L80)

## Custom Wait Utilities

The `utils/waits.py` module implements custom wait functions that enhance reliability compared to standard Selenium waits by incorporating automatic failure diagnostics and improved error reporting.

### wait_element
```python
def wait_element(driver, selector, by=By.CSS_SELECTOR, timeout=7):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, selector))
        )
    except TimeoutException:
        driver.save_screenshot(f"{driver.session_id}.png")
        raise AssertionError(f"Не дождался элемента: {selector}")
```
- **Purpose**: Waits for a single element to become visible
- **Improvements over standard waits**:
  - Automatic screenshot capture on timeout for debugging
  - Clear, descriptive error messages in English
  - Fixed 7-second timeout (optimized for test performance)
- **Usage**: Ideal for waiting for specific UI elements like buttons, inputs, or headers

### wait_all
```python
def wait_all(driver, selector, by=By.CSS_SELECTOR, timeout=7):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_all_elements_located((by, selector))
        )
    except TimeoutException:
        driver.save_screenshot(f"{driver.session_id}.png")
        raise AssertionError(f"Не дождался списка элементов: {selector}")
```
- **Purpose**: Waits for multiple elements matching a selector to become visible
- **Improvements**:
  - Screenshot capture on failure
  - Descriptive error messaging
  - Ensures all matching elements are visible, not just one
- **Usage**: Useful for waiting for lists, product grids, or table rows

### wait_title
```python
def wait_title(driver, title, timeout=7):
    try:
        WebDriverWait(driver, timeout).until(EC.title_is(title))
    except TimeoutException:
        raise AssertionError(f"Ожидал title='{title}', а был '{driver.title}'")
```
- **Purpose**: Waits for the page title to match the expected value
- **Improvements**:
  - Includes actual title in error message for easier debugging
  - Clear assertion error with expected vs actual values
- **Usage**: Verifies navigation to correct pages or successful form submissions

These custom waits improve test reliability by providing better failure diagnostics and consistent timeout values, reducing flakiness in automated tests.

**Section sources**
- [utils/waits.py](file://utils/waits.py#L0-L29)

## Docker-Based Test Environment

The `docker-compose.yml` file defines a containerized environment that enables isolated, reproducible test execution with all required services.

### Service Definitions

#### opencart
- **Image**: `agridyaev/opencart:4.0.2-3-debian-12-r33`
- **Ports**: 
  - 8081 → 8080 (HTTP)
  - 8443 → 8443 (HTTPS)
- **Environment Variables**:
  - Database connection details
  - Application host configuration
  - Empty password allowed for testing
- **Dependencies**: Depends on `mariadb` service
- **Health Check**: Uses curl to verify service availability with 10s interval, 5s timeout, 3 retries

#### mariadb
- **Image**: `bitnami/mariadb:11.2`
- **Ports**: 3306 → 3306 (database access)
- **Environment**:
  - Database name: `bitnami_opencart`
  - User: `bn_opencart`
  - Empty password allowed
- **Purpose**: Provides persistent storage for the OpenCart application

#### phpadmin
- **Image**: `phpmyadmin/phpmyadmin:latest`
- **Ports**: 8082 → 80 (web interface)
- **Environment**: Configured to connect to the `mariadb` service
- **Purpose**: Web-based database management interface for debugging and inspection

### Networking and Isolation
All services run on a default Docker network, enabling service discovery by name:
- OpenCart connects to MariaDB using hostname `mariadb`
- phpMyAdmin connects to the database using the same hostname
- External access through mapped ports (8081, 8082, 8443)

This configuration ensures:
- **Isolation**: Tests run in a clean environment, unaffected by external changes
- **Reproducibility**: Identical environment across different machines
- **Consistency**: Same OpenCart version and configuration for all tests
- **Ease of Setup**: Single command (`docker-compose up`) to start the complete test environment

**Section sources**
- [docker-compose.yml](file://docker-compose.yml#L0-L44)

## Usage Examples

### Test Consuming Multiple Fixtures
```python
def test_admin_login_page_po(browser, base_url, admin_path, admin_creds):
    if not admin_creds["user"] or not admin_creds["password"]:
        pytest.skip("Admin credentials required")
    
    login_page = LoginPage(browser).open_admin(base_url, admin_path)
    login_page.login(admin_creds["user"], admin_creds["password"])
    # Test assertions...
```
- **Fixture Chain**: `browser` → `base_url`, `admin_path`, `admin_creds`
- **Pattern**: All required dependencies injected via function parameters

### Test Using Custom Waits
```python
def test_product_page(browser, base_url):
    browser.get(base_url + "/product-url")
    wait_element(browser, "#button-cart")
    wait_all(browser, ".product-thumb")
    wait_title(browser, "Product Name - MyStore")
```
- **Advantage**: Automatic screenshots on failure, clear error messages
- **Reliability**: Reduces false positives from timing issues

### Environment Configuration
```bash
pytest --browser=chrome --headless \
       --base-url=http://localhost:8081 \
       --admin-username=admin \
       --admin-password=password \
       tests/
```
- **Integration**: CLI options map directly to fixtures in `conftest.py`
- **Flexibility**: Easy to switch between local, remote, or containerized environments

**Section sources**
- [conftest.py](file://conftest.py#L0-L80)
- [utils/waits.py](file://utils/waits.py#L0-L29)
- [tests/test_admin_login_po.py](file://tests/test_admin_login_po.py#L0-L19)
- [tests/test_product_page.py](file://tests/test_product_page.py#L0-L9)

## Performance Implications and Best Practices

### Performance Considerations
- **Fixture Scoping**: Session-scoped fixtures (`base_url`, `admin_creds`) reduce overhead by avoiding redundant setup
- **Browser Management**: Function-scoped `browser` fixture ensures test isolation but increases execution time
- **Wait Strategies**: Custom waits with 7-second timeout balance reliability and performance
- **Implicit vs Explicit Waits**: 2-second implicit wait reduces need for explicit waits in simple cases
- **Docker Overhead**: Container startup time adds to overall test suite duration

### Best Practices for Extension
1. **Adding New Fixtures**:
   - Use appropriate scope (session for expensive resources, function for isolated state)
   - Document dependencies and lifecycle clearly
   - Follow naming conventions

2. **Enhancing Wait Utilities**:
   - Add new wait conditions as needed (e.g., `wait_invisible`, `wait_text`)
   - Maintain consistent error reporting format
   - Consider parameterizing timeout values

3. **Extending Docker Configuration**:
   - Add caching layers for faster startup
   - Consider multi-stage builds for custom images
   - Implement volume mounting for persistent data

4. **Test Design**:
   - Use `wait` fixture for complex synchronization needs
   - Combine implicit and explicit waits judiciously
   - Leverage the `--headless` option for CI/CD environments

5. **Environment Management**:
   - Use environment variables for sensitive data
   - Maintain parity between test and production configurations
   - Regularly update base images for security patches

The current architecture supports extensibility while maintaining test reliability and performance.

**Section sources**
- [conftest.py](file://conftest.py#L0-L80)
- [utils/waits.py](file://utils/waits.py#L0-L29)
- [docker-compose.yml](file://docker-compose.yml#L0-L44)