# Getting Started

<cite>
**Referenced Files in This Document**  
- [conftest.py](file://conftest.py)
- [pytest.ini](file://pytest.ini)
- [docker-compose.yml](file://docker-compose.yml)
- [tests/test_main_page.py](file://tests/test_main_page.py)
- [pages/base.py](file://pages/base.py)
- [utils/waits.py](file://utils/waits.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installing Python Dependencies](#installing-python-dependencies)
4. [Configuring the Docker Environment](#configuring-the-docker-environment)
5. [Running Tests Without Docker](#running-tests-without-docker)
6. [Running Tests With Docker](#running-tests-with-docker)
7. [Understanding conftest.py: Browser Driver Initialization](#understanding-conftestpy-browser-driver-initialization)
8. [Understanding pytest.ini: Test Configuration](#understanding-pytestini-test-configuration)
9. [Executing Your First Test](#executing-your-first-test)
10. [Common Setup Pitfalls and Troubleshooting](#common-setup-pitfalls-and-troubleshooting)
11. [Expected Output Examples](#expected-output-examples)

## Introduction
This guide provides a comprehensive walkthrough for setting up and executing the automated test framework for OpenCart. It covers installation of required dependencies, configuration of the Docker-based test environment, execution of test suites, and troubleshooting common issues. The framework uses **Selenium** for browser automation and **Pytest** as the test runner, with support for multiple browsers and flexible configuration via command-line arguments.

## Prerequisites
Before beginning setup, ensure your system meets the following requirements:
- **Docker** and **Docker Compose** installed and running
- **Python 3.8+** with `pip` package manager
- Internet connection for downloading dependencies and Docker images
- Basic familiarity with command-line tools

## Installing Python Dependencies
The test framework relies on several Python packages. Install them using `pip`:

```bash
pip install selenium pytest
```

These packages are essential for:
- **Selenium**: Browser automation and interaction with web elements
- **Pytest**: Test discovery, execution, and reporting

No `requirements.txt` is present in the project, so manual installation of these core dependencies is required. Ensure versions are compatible:
- Selenium ≥ 4.0
- Pytest ≥ 7.0

## Configuring the Docker Environment
The project includes a `docker-compose.yml` file that defines a complete OpenCart test environment consisting of:
- **opencart**: OpenCart application server (port 8081)
- **mariadb**: Database backend (port 3306)
- **phpadmin**: phpMyAdmin interface (port 8082)

To start the environment:

```bash
docker-compose up -d
```

This command:
- Pulls the specified container images
- Starts all services in detached mode
- Maps ports for external access
- Waits for health checks to pass

Verify all containers are running:

```bash
docker-compose ps
```

All services should show status `Up` and pass health checks.

**Diagram sources**  
- [docker-compose.yml](file://docker-compose.yml#L1-L44)

## Running Tests Without Docker
You can run tests against any OpenCart instance, including local or remote deployments. Use the `--base-url` parameter to specify the target:

```bash
pytest tests/test_main_page.py --browser=chrome --base-url=http://localhost:8081
```

This approach:
- Launches a local browser instance (Chrome by default)
- Navigates to the specified URL
- Executes test cases without relying on Dockerized services

Ensure the target OpenCart instance is accessible and responsive before running tests.

## Running Tests With Docker
Once the Docker environment is up, run tests against the local OpenCart instance:

```bash
docker-compose up -d  # Start services
pytest tests/test_main_page.py --browser=chrome --base-url=http://localhost:8081
```

The `--base-url=http://localhost:8081` matches the exposed port in `docker-compose.yml`. This setup ensures:
- Consistent test environment
- Isolated database state
- Repeatable test execution

To stop the environment after testing:

```bash
docker-compose down
```

## Understanding conftest.py: Browser Driver Initialization
The `conftest.py` file defines pytest fixtures that configure the test environment. Key components include:

- **`pytest_addoption`**: Adds command-line options for browser selection, base URL, admin credentials, and headless mode
- **`browser` fixture**: Initializes the WebDriver instance based on the selected browser
- **`base_url`, `admin_path`, `admin_creds`**: Session-scoped fixtures for shared configuration
- **`wait` fixture**: Provides WebDriverWait instances for explicit waits

Supported browsers:
- **Chrome**: Default, with optional headless mode (`--headless`)
- **Firefox**: Full support with window sizing
- **Safari**: Limited to macOS environments

The fixture automatically handles driver lifecycle (setup and teardown), ensuring clean browser instances for each test.

**Section sources**  
- [conftest.py](file://conftest.py#L10-L80)

## Understanding pytest.ini: Test Configuration
The `pytest.ini` file configures global test behavior:

```ini
[pytest]
addopts = -v -s --tb=short
markers =
    admin: mark tests that require admin login
```

This configuration:
- Enables verbose output (`-v`)
- Allows print statements in tests (`-s`)
- Shortens traceback format (`--tb=short`)
- Defines a custom marker `@pytest.mark.admin` for admin-specific tests

These settings ensure readable output and logical test categorization.

**Section sources**  
- [pytest.ini](file://pytest.ini#L1-L5)

## Executing Your First Test
Run a basic test to verify the setup:

```bash
# Run a single test file
pytest tests/test_main_page.py --browser=chrome -v

# Run in headless mode
pytest tests/test_main_page.py --browser=chrome --headless -v

# Run admin tests with credentials
OC_ADMIN_USER=admin OC_ADMIN_PASS=password pytest tests/test_admin_login.py --browser=firefox
```

Example command breakdown:
- `tests/test_main_page.py`: Target test file
- `--browser=chrome`: Use Chrome browser
- `--headless`: Run without GUI (useful for CI)
- `-v`: Verbose output

Successful execution will show test results with `PASSED` status.

## Common Setup Pitfalls and Troubleshooting
### Missing WebDriver Executables
**Issue**: `WebDriver not found` or `Service executable not found`  
**Solution**: Ensure ChromeDriver or GeckoDriver is installed and in PATH, or use browsers with built-in driver management (Chrome, Firefox).

### Browser Version Incompatibility
**Issue**: `SessionNotCreatedException` or `Driver version mismatch`  
**Solution**: Update browser and WebDriver to compatible versions. Consider using Dockerized browsers in CI environments.

### Docker Network Issues
**Issue**: `Connection refused` or `timeout` when accessing http://localhost:8081  
**Solution**:  
- Verify `docker-compose ps` shows all services as `Up`  
- Check logs: `docker-compose logs opencart`  
- Wait for health check completion (may take 1–2 minutes)

### Headless Mode Rendering Issues
**Issue**: Elements not found in headless mode but work in headed mode  
**Solution**:  
- Increase implicit wait time  
- Use explicit waits (`wait` fixture)  
- Ensure window size is set (done automatically in `conftest.py`)

### Environment Variable Not Set
**Issue**: Admin tests fail due to empty credentials  
**Solution**: Export variables:
```bash
export OC_ADMIN_USER=admin
export OC_ADMIN_PASS=password
```

## Expected Output Examples
Successful test run output:
```
tests/test_main_page.py::test_title PASSED
tests/test_main_page.py::test_currency_dropdown PASSED
================= 2 passed in 12.34s =================
```

Failed test example:
```
tests/test_admin_login.py::test_valid_login FAILED
...
E       selenium.common.exceptions.TimeoutException: Message: 
```

Verbose output (`-v`) shows each test case and result, while `-s` allows print statements to appear in the console.

**Section sources**  
- [conftest.py](file://conftest.py#L1-L80)
- [pytest.ini](file://pytest.ini#L1-L5)
- [docker-compose.yml](file://docker-compose.yml#L1-L44)