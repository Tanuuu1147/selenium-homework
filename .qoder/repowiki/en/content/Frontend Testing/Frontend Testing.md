# Frontend Testing

<cite>
**Referenced Files in This Document**   
- [main_page.py](file://pages/main_page.py)
- [category_page.py](file://pages/category_page.py)
- [product_page.py](file://pages/product_page.py)
- [login_page.py](file://pages/login_page.py)
- [register_page.py](file://pages/register_page.py)
- [currency_dropdown.py](file://pages/components/currency_dropdown.py)
- [base.py](file://pages/base.py)
- [test_main_page_po.py](file://tests/test_main_page_po.py)
- [test_register_po.py](file://tests/test_register_po.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Page Objects](#core-page-objects)
   - [MainPage](#mainpage)
   - [CategoryPage](#categorypage)
   - [ProductPage](#productpage)
   - [LoginPage](#loginpage)
   - [RegisterPage](#registerpage)
3. [Reusable UI Components](#reusable-ui-components)
   - [CurrencyDropdown](#currencydropdown)
4. [Test Implementation Examples](#test-implementation-examples)
5. [Extensibility and Customization](#extensibility-and-customization)
6. [Conclusion](#conclusion)

## Introduction
This document details the frontend testing framework for OpenCart, focusing on page object model (POM) implementation. The framework encapsulates user-facing pages and reusable components to enable reliable, maintainable, and scalable end-to-end tests. Each page object abstracts DOM interactions, providing a clean API for test scripts while isolating locators and interaction logic.

The design follows Selenium best practices with explicit waits, robust element interaction strategies, and extensible base classes. This structure supports testing across different OpenCart themes and customizations with minimal changes.

## Core Page Objects

### MainPage
Represents the homepage of the OpenCart storefront. It provides methods to interact with core navigation and discovery elements.

Key attributes:
- `TITLE`: Expected page title for validation
- `LOGO`, `SEARCH`, `CART`, `PRODUCT_TILES`: Locator strategies using CSS selectors with fallbacks for theme variations

Primary method:
- `open_home(base_url)`: Navigates to the store root URL

This page object enables verification of essential UI components and ensures baseline storefront functionality.

**Section sources**
- [main_page.py](file://pages/main_page.py#L1-L12)

### CategoryPage
Encapsulates interactions within product category listings. Supports browsing and filtering operations.

Key attributes:
- `BREADCRUMB`, `LEFT_MENU`, `SORT`, `LIMIT`, `PRODUCT_TILES`: Locators for category navigation and product grid

Primary method:
- `open_by_path(base_url, path)`: Opens a specific category using the path parameter

Enables testing of category navigation, product filtering, and layout consistency.

**Section sources**
- [category_page.py](file://pages/category_page.py#L1-L14)

### ProductPage
Handles product detail views and cart interactions. Central to validating product information and purchase flows.

Key attributes:
- `TITLE_H1`, `BUTTON_CART`, `QTY`, `TABS`, `PRICE_BLOCK`: Locators for product details and add-to-cart functionality

Primary method:
- `open_by_id(base_url, path, product_id)`: Opens a specific product page using route parameters

Supports validation of pricing, descriptions, and successful addition to cart.

**Section sources**
- [product_page.py](file://pages/product_page.py#L1-L13)

### LoginPage
Manages administrator authentication flow in the backend.

Key attributes:
- `USERNAME`, `PASSWORD`, `SUBMIT`: Locators for login form fields

Primary methods:
- `open_admin(base_url, admin_path)`: Navigates to admin login page
- `login(user, password)`: Performs authentication with input typing and submission

Provides reliable admin session establishment for backend testing.

**Section sources**
- [login_page.py](file://pages/login_page.py#L1-L15)

### RegisterPage
Handles customer account creation with dynamic form handling and error resilience.

Key attributes:
- `FIRSTNAME`, `LASTNAME`, `EMAIL`, `TELEPHONE`, `PASSWORD`, `AGREE`, `SUBMIT`, `SUCCESS_HEADING`: Comprehensive form field locators
- `AGREE_LABEL`: Alternative locator for agreement checkbox label

Key methods:
- `open_register(base_url)`: Navigates to registration page
- `_type_if_present(locator, text)`: Safely types into optional fields
- `_type_confirm_password(password)`: Handles varying confirm password field implementations
- `_ensure_agree_checked()`: Robustly checks agreement checkbox via label click if direct click fails
- `register(firstname, lastname, email, password)`: Orchestrates full registration flow with error detection
- `_wait_success_or_errors(timeout)`: Waits for success indicators or captures error messages

Implements defensive programming to handle theme-specific variations in form structure.

**Section sources**
- [register_page.py](file://pages/register_page.py#L1-L99)

## Reusable UI Components

### CurrencyDropdown
A reusable component for handling currency selection in the storefront header.

Key attributes:
- `TOGGLE`, `MENU`: Locators for dropdown trigger and menu

Primary method:
- `choose_currency(currency_name)`: Opens dropdown and selects currency by visible text

Demonstrates component encapsulation for shared UI elements, promoting code reuse across page objects.

**Section sources**
- [currency_dropdown.py](file://pages/components/currency_dropdown.py#L1-L11)

## Test Implementation Examples

### MainPage Test Case
Validates presence of core homepage elements and correct page title.

```python
def test_main_page_elements_po(browser, base_url):
    page = MainPage(browser).open_home(base_url)
    page.wait_visible(MainPage.LOGO)
    page.wait_visible(MainPage.SEARCH)
    page.wait_visible(MainPage.CART)
    page.wait_visible(MainPage.PRODUCT_TILES)
    assert browser.title == MainPage.TITLE
```

Demonstrates basic page navigation, element visibility checks, and state assertion using the page object's locator constants.

**Section sources**
- [test_main_page_po.py](file://tests/test_main_page_po.py#L1-L9)

### RegisterPage Test Case
Tests successful user registration with dynamic email generation.

```python
def test_register_new_user_po(browser, base_url):
    email = f"user_{int(time.time())}@mail.com"
    page = RegisterPage(browser).open_register(base_url)
    try:
        heading = page.register("Test", "User", email, "password123")
    except AssertionError as e:
        pytest.fail(f"Registration failed: {e}")
    assert "Your Account Has Been Created!" in heading.text
```

Illustrates form submission, success validation, and error handling through the page object's robust registration method.

**Section sources**
- [test_register_po.py](file://tests/test_register_po.py#L1-L13)

## Extensibility and Customization
To adapt these page objects for new OpenCart themes or customizations:

1. **Override Locators**: Inherit from existing page classes and redefine locator tuples to match new HTML structure
2. **Extend Methods**: Add new methods for theme-specific features while maintaining core functionality
3. **Component Reuse**: Leverage `CurrencyDropdown` and similar components across multiple page objects
4. **Base Class Utilization**: All page objects inherit from `BasePage`, which provides standardized interaction methods (`click`, `type`, `wait_visible`, etc.) with built-in scroll-to-view fallbacks for non-clickable elements

The framework's modular design allows seamless integration of new pages and components while maintaining consistency in test implementation patterns.

**Section sources**
- [base.py](file://pages/base.py#L1-L35)
- [main_page.py](file://pages/main_page.py#L1-L12)
- [register_page.py](file://pages/register_page.py#L1-L99)

## Conclusion
The frontend testing framework provides a robust foundation for automated testing of OpenCart storefront and administrative functionality. Through well-structured page objects and reusable components, it enables reliable test automation that can adapt to various themes and custom implementations. The combination of resilient element interaction strategies and clear separation of concerns makes this framework suitable for both basic validation and complex end-to-end scenarios.