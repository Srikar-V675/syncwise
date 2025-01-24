import json

from gradesync.models import Score
from utils.driver import initialise_driver
from utils.redis_conn import (
    incr_scraping_progress,
    invalidate_scraping_redis_key,
    log_scraping_errors,
)
from utils.scraper import scrape_result, status_code_str


def scrape_bg_task(semester, students, redis_name, result_url):
    try:
        scores, errors = [], []
        print(semester, flush=True)
        for stud in students:
            usn = stud.usn
            score, code = scrape_student(usn, result_url)
            # score = json.loads(score)["Marks"]
            if not check_and_append_error(usn=usn, errors=errors, code=code):
                score = json.loads(score)["Marks"]
                scores.append(
                    Score(student=stud, semester=semester, marks=json.dumps(score))
                )
            incr_scraping_progress(redis_name)

        log_scraping_errors(name=redis_name, errors=errors)
        batch_add_scores(scores=scores)

    except Exception as e:
        invalidate_scraping_redis_key(name=redis_name)
        raise e


def scrape_student(usn, result_url):
    try:
        driver = initialise_driver()
        print(f"Scraping for usn: {usn}", flush=True)
        return scrape_result(USN=usn, url=result_url, driver=driver)
    except Exception as e:
        raise e


def check_error(code):
    if code > 0:
        return True
    else:
        return False


def append_error(usn, errors, code):
    print(f"Error: {usn} -> {status_code_str(code)}", flush=True)
    errors.append(
        {
            "usn": usn,
            "error": status_code_str(code),
        }
    )


def check_and_append_error(usn, errors, code):
    if check_error(code):
        append_error(usn=usn, errors=errors, code=code)
        return True
    else:
        return False


def batch_add_scores(scores):
    try:
        Score.objects.bulk_create(scores)
    except Exception as e:
        raise e
