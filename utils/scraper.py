import json
import time
from typing import Optional, Tuple

import webExtractor.trueCaptcha as trueCaptcha
from pydantic import HttpUrl
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webExtractor.driver import initialise_driver


# Function to solve captcha using trueCaptcha
def solve_captcha(driver) -> str:
    """
    Solves the captcha on a webpage using an image-based captcha solver.

    Args:
        driver: WebDriver object representing the browser driver.

    Returns:
        str: The solved captcha string.
        int:

    Description:
        This function finds the captcha image element on the webpage, takes a screenshot
        of the captcha image, and then passes the image to the trueCaptcha solver to
        extract the captcha text. The solved captcha string is returned.
    """
    # Find the captcha image element on the webpage
    div_element = driver.find_element("xpath", '//*[@id="raj"]/div[2]/div[2]/img')

    # Take a screenshot of the captcha image
    div_element.screenshot(r"/api/webExtractor/captcha.png")

    # Solve the captcha using the trueCaptcha solver
    captcha = trueCaptcha.solve_captcha(
        "/api/webExtractor/captcha.png",
    )

    return captcha


def refresh_captcha(driver) -> str:
    refresh_button = WebDriverWait(driver, 4).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/div[2]/div[1]/div[2]/div/div[2]/form/div/div[2]/div[2]/div[3]/p/a",
            )
        )
    )
    refresh_button.click()
    captcha = solve_captcha(driver)
    return captcha


async def scrape_results(
    USN: str, result_url: HttpUrl, driver
) -> Tuple[Optional[str], int]:
    """
    Scrape the results of a student with the given USN.

    Args:
        USN (str): The University Seat Number (USN) of the student.
        link (str): The link to the VTU results website.
        driver: WebDriver object representing the browser driver.

    Returns:
        str: JSON string representing the student's details and marks or None if the results are not available.
        int: The status code of the request.
            0: Success
            1: Invalid USN or non-existent USN
            2: Invalid captcha
            3: Connection Timeout
            4: Connection refused
            5: Other WebDriverException
            6: Other Exception
            >10: 10 + reattempts for invalid captcha
            >20: 20 + reattempts for connection timeout

    Description:
        This function navigates to the VTU results website, fills in the USN and captcha
        fields, submits the form, and retrieves the student's results if available. It
        handles cases such as invalid captcha codes and alerts indicating unavailable
        results. The student's details and marks are extracted, formatted into a dictionary,
        converted to a JSON string, and returned.
    """
    print("Scraping results for USN:", USN, flush=True)
    invalid_count = 0
    error_count = 0
    refused_count = 0

    while True:
        try:
            # Navigate to the VTU results website
            url = str(result_url)

            driver.get(url)

            # solve the captcha
            captcha = solve_captcha(driver)

            # Refresh captcha if length is not 6
            if len(captcha) != 6:
                captcha = refresh_captcha(driver)

            # Fill in the USN and captcha fields
            usn_text_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "lns"))
            )
            usn_text_field.send_keys(USN)

            captcha_text_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "captchacode"))
            )
            captcha_text_field.send_keys(captcha)

            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "submit"))
            )
            submit_button.click()

            # Check for alerts
            if EC.alert_is_present()(driver):
                alert = driver.switch_to.alert
                if (
                    alert.text
                    == "University Seat Number is not available or Invalid..!"
                ):
                    print(f"Invalid USN {USN}", flush=True)
                    alert.accept()
                    return None, 1
                elif alert.text == "Invalid captcha code !!!":
                    print("Invalid captcha code for " + USN, flush=True)
                    print("Reattempting for " + USN, flush=True)
                    alert.accept()
                    invalid_count += 1
                    if invalid_count == 3:
                        return None, 2
                    continue
                elif alert.text == "Please check website after 2 hour !!!":
                    print("Website cool down...", flush=True)
                    alert.accept()
                    print("Reinitialising driver to bypass cool down...", flush=True)
                    print("Reattempting after 10sec...", flush=True)
                    time.sleep(10)
                    driver = initialise_driver()
                    continue

            else:
                # Wait for student details
                WebDriverWait(driver, 4).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[1]/td[2]",
                        )
                    )
                )
                # old XPATH: "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[1]/td[2]"
                # Extract student details and marks
                usn_element = driver.find_element(
                    By.XPATH,
                    "/html/body/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[1]/td[2]",
                )
                # old usn XPATH: "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[1]/td[2]"
                stud_element = driver.find_element(
                    By.XPATH,
                    "/html/body/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[2]/td[2]",
                )
                # old stud XPATH: "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/table/tbody/tr[2]/td[2]"
                table_element = driver.find_element(
                    By.XPATH,
                    "/html/body/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[2]/div/div/div[2]/div",
                )
                # old table XPATH: "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div/div[2]/div"
                sub_elements = table_element.find_elements(By.XPATH, "div")
                num_sub_elements = len(sub_elements)
                stud_text = stud_element.text
                usn_text = usn_element.text
                print("Student Name: " + stud_text + " | USN: " + usn_text.upper())

                # Extract marks for each subject
                marks_list = []
                for i in range(2, num_sub_elements + 1):
                    marks_data = []
                    for j in range(1, 7):
                        details = driver.find_element(
                            By.XPATH,
                            "/html/body/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div/div[2]/div/div/div[2]/div/div["
                            + str(i)
                            + "]/div["
                            + str(j)
                            + "]",
                        )
                        marks_data.append(details.text)
                    marks_details = {
                        "Subject Code": marks_data[0],
                        "Subject Name": marks_data[1],
                        "INT": marks_data[2],
                        "EXT": marks_data[3],
                        "TOT": marks_data[4],
                        "Result": marks_data[5],
                    }

                    marks_list.append(marks_details)

                marks_list.sort(key=lambda x: x["Subject Code"])

                # Construct student data dictionary
                student_data = {
                    "USN": usn_text.upper(),
                    "Name": stud_text.upper(),
                    "Marks": marks_list,
                }

                # Convert the dictionary to a JSON object
                student_data = json.dumps(student_data, indent=4)

                if invalid_count > 0:
                    return student_data, 10 + invalid_count
                elif invalid_count == 0:
                    return student_data, 0
                elif error_count > 0:
                    return student_data, 20 + error_count
                elif error_count == 0:
                    return student_data, 0

        except WebDriverException as e:
            if "ERR_CONNECTION_TIMED_OUT" in str(e):
                print("Connection timed out.", flush=True)
                error_count += 1
                if error_count == 3:
                    return None, 3
                continue
            elif "ERR_CONNECTION_REFUSED" in str(e):
                print("Connection refused.", flush=True)
                time.sleep(5)
                driver = initialise_driver()
                refused_count += 1
                if refused_count == 3:
                    return None, 4
                continue
            else:
                # Handle other WebDriverExceptions if needed
                print("WebDriverException:", e, flush=True)
                return None, 5
        except Exception as e:
            # Handle other exceptions if needed
            print("Exception:", e, flush=True)
            return None, 6
