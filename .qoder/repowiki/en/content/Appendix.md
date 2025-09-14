# Appendix

<cite>
**Referenced Files in This Document**   
- [config.php](file://opencart_data/config.php)
- [administration/config.php](file://opencart_data/administration/config.php)
- [conftest.py](file://conftest.py)
- [pytest.ini](file://pytest.ini)
- [waits.py](file://utils/waits.py)
- [docker-compose.yml](file://docker-compose.yml)
- [test_scenarios.py](file://tests/test_scenarios.py)
</cite>

## Table of Contents
1. [OpenCart Version Compatibility](#opencart-version-compatibility)
2. [Known Limitations of the Test Framework](#known-limitations-of-the-test-framework)
3. [Contribution Guidelines](#contribution-guidelines)
4. [External Documentation and Tooling References](#external-documentation-and-tooling-references)
5. [Data Privacy Considerations](#data-privacy-considerations)
6. [Upgrade Paths for Future OpenCart Versions](#upgrade-paths-for-future-opencart-versions)

## OpenCart Version Compatibility

The test framework is configured to work with OpenCart version **4.0.2**, as specified in the `docker-compose.yml` file under the `opencart` service image tag (`agridyaev/opencart:4.0.2-3-debian-12-r33`). This version is consistent with the configuration files located in the `opencart_data` directory, which define application paths, database settings, and server URLs aligned with OpenCart's standard directory structure.

Both frontend (Catalog) and backend (Admin) configurations are present and correctly mapped to the expected environment running on `http://localhost:8081`. The `HTTP_SERVER` and `HTTPS_SERVER` values in both `config.php` and `administration/config.php` confirm local deployment targeting port 8081, matching the Docker service exposure.

**Section sources**
- [docker-compose.yml](file://docker-compose.yml#L34-L41)
- [opencart_data/config.php](file://opencart_data/config.php#L4-L7)
- [opencart_data/administration/config.php](file://opencart_data/administration/config.php#L4-L7)

## Known Limitations of the Test Framework

The current test framework has several known limitations:

- **Unsupported OpenCart Extensions**: The framework does not include test coverage or component mappings for third-party OpenCart extensions. Custom modules or plugins installed in a production environment may not be accessible or verifiable through the existing page objects.
  
- **Browser-Specific Quirks**: While Chrome, Firefox, and Safari are supported via the `--browser` flag in `conftest.py`, Safari lacks support for headless mode and advanced configuration options, potentially leading to inconsistent execution behavior across platforms.

- **Missing Admin Features in Page Objects**: Although admin login and product management tests exist (e.g., `test_admin_login.py`, `test_admin_products_po.py`), not all administrative functionalities (such as user roles, extensions, or reports) are fully implemented in the page object model.

- **Dynamic Element Detection**: Some elements like the cart indicator or currency menu use heuristic search patterns (e.g., multiple CSS selectors) due to theme-dependent variations, which may reduce reliability if OpenCart themes change significantly.

**Section sources**
- [conftest.py](file://conftest.py#L45-L80)
- [test_scenarios.py](file://tests/test_scenarios.py#L23-L61)
- [pages/admin/admin_login_page.py](file://pages/admin/admin_login_page.py)
- [pages/admin/admin_products_page.py](file://pages/admin/admin_products_page.py)

## Contribution Guidelines

Contributors are expected to adhere to the following standards:

### Code Style
- Follow PEP 8 guidelines for Python code formatting.
- Use descriptive variable and function names.
- Maintain consistency with existing page object design patterns (e.g., separation of page logic from test logic).
- Include docstrings for all functions and classes.

### Test Coverage Expectations
- All new features must be accompanied by corresponding automated tests.
- Tests should cover both positive and negative scenarios.
- Page object methods should abstract interactions and include explicit waits using utilities from `waits.py`.

### Pull Request Workflow
1. Fork the repository and create a feature branch.
2. Implement changes with clear, atomic commits.
3. Ensure all tests pass locally using the Docker environment.
4. Submit a pull request with a detailed description of changes and motivation.
5. Await review and address feedback before merging.
6. Merge only after approval and successful CI execution (if applicable).

**Section sources**
- [utils/waits.py](file://utils/waits.py#L1-L30)
- [pytest.ini](file://pytest.ini#L1-L5)
- [conftest.py](file://conftest.py#L1-L44)

## External Documentation and Tooling References

The following external resources are essential for development and troubleshooting:

- **OpenCart API Documentation**: [https://www.opencart.com/](https://www.opencart.com/) — Official site and documentation for OpenCart features, extensions, and core architecture.
- **Selenium WebDriver (Python)**: [https://selenium-python.readthedocs.io/](https://selenium-python.readthedocs.io/) — Comprehensive guide to Selenium WebDriver usage, expected conditions, and browser interactions.
- **Pytest Documentation**: [https://docs.pytest.org/](https://docs.pytest.org/) — Reference for markers, fixtures, command-line options, and configuration.
- **Docker Compose**: [https://docs.docker.com/compose/](https://docs.docker.com/compose/) — Configuration and orchestration of multi-container environments.

These tools are integrated into the project via `docker-compose.yml`, `conftest.py`, and `pytest.ini`, enabling reproducible testing environments and standardized execution.

**Section sources**
- [docker-compose.yml](file://docker-compose.yml#L1-L41)
- [conftest.py](file://conftest.py#L1-L80)
- [pytest.ini](file://pytest.ini#L1-L5)

## Data Privacy Considerations

Sensitive data handling must follow these principles:

- **Credentials Management**: Admin credentials are passed via environment variables (`OC_ADMIN_USER`, `OC_ADMIN_PASS`) and accessed through `os.getenv()` in `conftest.py`, preventing hardcoding in source files.
- **Test Artifacts**: Screenshots captured on failure (e.g., `driver.save_screenshot(f"{driver.session_id}.png")`) are stored locally and should be excluded from version control via `.gitignore`.
- **No Real User Data**: Test scenarios should use synthetic or anonymized data. Avoid using real customer information in test inputs or assertions.
- **Session Isolation**: Each test runs in an isolated browser session, and sessions are terminated after test completion via `driver.quit()`.

Ensure compliance with data protection regulations (e.g., GDPR) when extending the framework to environments with access to production-like data.

**Section sources**
- [conftest.py](file://conftest.py#L60-L65)
- [utils/waits.py](file://utils/waits.py#L10-L12)

## Upgrade Paths for Future OpenCart Versions

To support future OpenCart versions:

1. **Update Docker Image**: Modify the `opencart` service image in `docker-compose.yml` to target the desired version tag.
2. **Verify Configuration Paths**: Confirm that `config.php` and `administration/config.php` paths and constants remain compatible.
3. **Update Selectors**: Audit and update CSS selectors in page objects and utility functions (e.g., `_get_cart_indicator_text`) to reflect any DOM changes.
4. **Test Admin Interface Changes**: Validate that admin login flow, navigation, and product management interfaces have not changed significantly.
5. **Extend Page Objects**: Add new page classes or methods to cover newly introduced features or redesigned components.
6. **Regression Testing**: Run full test suite to ensure backward compatibility and identify breaking changes early.

Automated visual regression tools or schema comparison utilities can assist in identifying structural changes between versions.

**Section sources**
- [docker-compose.yml](file://docker-compose.yml#L34-L41)
- [opencart_data/config.php](file://opencart_data/config.php)
- [opencart_data/administration/config.php](file://opencart_data/administration/config.php)
- [test_scenarios.py](file://tests/test_scenarios.py#L23-L61)