from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException, TimeoutException
import time

# ---------- Browser setup ----------
options = Options()
# options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
driver.get("https://web.telegram.org/k/")

print("Please log in manually and navigate to the chat where messages are highlighted.")
print("The script will start processing when you press Enter.")
input("Press Enter to continue...")

# ---------- Helper functions ----------
def click_delete_menu_item():
    """Click the 'Delete' item in the right‑click context menu."""
    try:
        delete_item = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[contains(@class, 'btn-menu-item') and contains(@class, 'danger')][.//span[text()='Delete']]"
            ))
        )
        delete_item.click()
        print("  -> Clicked 'Delete' in menu.")
        return True
    except TimeoutException:
        print("  Delete menu item not found or not clickable.")
        return False
    except Exception as e:
        print(f"  Error clicking Delete menu item: {e}")
        return False

def check_delete_for_all():
    """Check the 'Delete for all members' checkbox if it exists; skip if not."""
    try:
        checkbox_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//span[text()='Delete for all members']/preceding-sibling::input[@type='checkbox']"
            ))
        )
        driver.execute_script("arguments[0].click();", checkbox_input)
        print("  -> Checked 'Delete for all members'.")
        return True
    except:
        print("  -> No 'Delete for all members' checkbox (not needed).")
        return True

def click_final_delete():
    """Click the big red 'Delete' button in the final confirmation popup."""
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'popup')]"))
        )
    except:
        print("  Popup did not appear.")
        return False

    time.sleep(0.5)

    locators = [
        (By.XPATH, "//button[contains(@class, 'popup-button') and contains(@class, 'danger')]"),
        (By.XPATH, "//button[normalize-space(text())='Delete']"),
        (By.XPATH, "//div[contains(@class, 'popup')]//button[.//*[contains(text(), 'Delete')]]"),
    ]

    for by, locator in locators:
        try:
            button = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((by, locator))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", button)
            print("  -> Clicked final 'Delete'.")
            return True
        except:
            continue

    print("  Could not find the final Delete button.")
    return False

def click_up_arrow():
    """Click the up arrow button to navigate to the previous highlighted message."""
    try:
        back_arrow_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.topbar-search-input-arrow"))
        )
        back_arrow_btn.click()
        print("  -> Clicked up arrow.")
        return True
    except Exception as e:
        print(f"  Up arrow click failed: {e}")
        try:
            back_arrow_btn = driver.find_element(By.CSS_SELECTOR, "button.topbar-search-input-arrow")
            driver.execute_script("arguments[0].click();", back_arrow_btn)
            print("  -> Clicked up arrow via JavaScript.")
            return True
        except:
            return False

def right_click_bubble(bubble):
    """
    Right‑click on the bubble element.
    Tries ActionChains first, then falls back to JavaScript.
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", bubble)
        time.sleep(0.3)

        # Attempt 1: ActionChains (most reliable for custom context menus)
        ActionChains(driver).context_click(bubble).perform()
        return True
    except Exception as e:
        print(f"  ActionChains right‑click failed: {e}")
        # Attempt 2: JavaScript contextmenu event
        try:
            driver.execute_script("""
                var evt = new MouseEvent('contextmenu', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                arguments[0].dispatchEvent(evt);
            """, bubble)
            return True
        except Exception as e2:
            print(f"  JavaScript right‑click failed: {e2}")
            return False

def delete_message(bubble, mid):
    """
    Attempt to delete a single highlighted message.
    Right‑click only on the bubble itself.
    """
    # Right‑click on the bubble
    if not right_click_bubble(bubble):
        print("  Could not right‑click on bubble.")
        return False

    # Wait for the Delete menu item to appear
    if click_delete_menu_item():
        return True

    # If not found, wait a bit and retry once
    time.sleep(0.5)
    if click_delete_menu_item():
        return True

    # Still no Delete button – maybe the menu didn't open; try JavaScript right‑click again
    print("  Retrying right‑click with JavaScript...")
    if not right_click_bubble(bubble):
        return False
    time.sleep(0.5)
    if click_delete_menu_item():
        return True

    return False

# ---------- Main loop ----------
processed_ids = set()
poll_interval = 0.5
max_retries = 2

def process_highlighted():
    while True:
        try:
            # Re‑fetch highlighted messages each iteration
            divs = driver.find_elements("css selector", "div.bubble.is-highlighted")
            for div in divs:
                try:
                    mid = div.get_attribute("data-mid")
                    if not mid or mid in processed_ids:
                        continue

                    print(f"\n--- Attempting to delete message mid={mid} ---")

                    success = False
                    for attempt in range(max_retries):
                        print(f"Attempt {attempt+1}/{max_retries}")
                        if delete_message(div, mid):
                            # Proceed with checkbox and final delete
                            time.sleep(1.0)
                            if not check_delete_for_all():
                                continue
                            if not click_final_delete():
                                continue

                            time.sleep(1.5)  # deletion completion
                            click_up_arrow()
                            time.sleep(0.5)

                            success = True
                            break
                        else:
                            time.sleep(1.0)  # wait before retry

                    if success:
                        processed_ids.add(mid)
                        print(f"Successfully deleted mid={mid}")
                    else:
                        print(f"Failed to delete mid={mid} after {max_retries} attempts. Skipping.")
                        processed_ids.add(mid)

                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    print(f"Error while processing a div: {e}")
                    continue

        except WebDriverException as e:
            print(f"Browser/session error, retrying: {e}")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped by user.")
            break

        time.sleep(poll_interval)

# Start the process
try:
    process_highlighted()
finally:
    driver.quit()