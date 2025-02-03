from gradesync.models import (
    Score,
    SemesterMetrics,
    StudentPerformance,
    Subject,
    SubjectMetrics,
)
from utils.driver import initialise_driver
from utils.redis_conn import (
    incr_scraping_progress,
    invalidate_scraping_redis_key,
    log_scraping_errors,
)
from utils.scraper import scrape_result, status_code_str


def scrape_bg_task(semester, students, redis_name, result_url):
    try:
        errors = []
        print(semester, flush=True)
        for student in students:
            usn = student.usn
            score, code = scrape_student(usn, result_url)
            if not check_and_append_error(usn=usn, errors=errors, code=code):
                add_scores_and_update_metrics(semester, student, scores=score["Marks"])
            incr_scraping_progress(redis_name)

        update_semester_metrics(semester, student.section)
        log_scraping_errors(name=redis_name, errors=errors)

    except Exception as e:
        invalidate_scraping_redis_key(name=redis_name)
        raise e


def add_scores_and_update_metrics(semester, student, scores):
    try:
        subjects, existing_scores = fetch_related_objects(semester, student)
        batch_add_scores(student, semester, scores, subjects, existing_scores)
        update_subject_metrics(subjects, semester, student.section)
    except Exception as e:
        raise e


def calculate_grade(total, result_code):
    """Calculate the grade based on total marks and result code."""
    if result_code == "P":
        if total >= 75:
            return "FCD"
        elif total >= 60:
            return "FC"
        return "SC"
    return result_code


def fetch_related_objects(semester, student):
    """Prefetch subjects and existing scores."""
    subjects = {
        subject.sub_code: subject
        for subject in Subject.objects.filter(semester=semester)
    }
    existing_scores = {
        (score.subject.sub_code, score.subject.semester): score
        for score in Score.objects.filter(student=student, semester=semester)
    }
    return subjects, existing_scores


def handle_score_update_or_create(
    s, subjects, student, existing_scores, marks_new, marks_update
):
    """Handle the logic for updating or creating scores."""
    sub_code = s["Subject Code"]
    internal = int(s["INT"])
    external = int(s["EXT"])
    total = int(s["TOT"])
    result_code = s["Result"]

    grade = calculate_grade(total, result_code)

    subject = subjects.get(sub_code)
    if not subject:
        raise ValueError(f"Subject with code {sub_code} not found for semester.")

    score_key = (subject.sub_code, subject.semester)
    if score_key in existing_scores:
        score_obj = existing_scores[score_key]
        score_obj.internal = internal
        score_obj.external = external
        score_obj.total = total
        score_obj.grade = grade
        marks_update.append(score_obj)
    else:
        marks_new.append(
            Score(
                student=student,
                semester=subject.semester,
                subject=subject,
                internal=internal,
                external=external,
                total=total,
                grade=grade,
            )
        )


def process_scores(marks_new, marks_update):
    """Bulk create or update scores."""
    if marks_new:
        Score.objects.bulk_create(marks_new)
    if marks_update:
        Score.objects.bulk_update(
            marks_update, ["internal", "external", "total", "grade"]
        )


def update_student_performance(student, semester):
    """Update or create student performance."""
    student_performance, _ = StudentPerformance.objects.get_or_create(
        student=student, semester=semester
    )
    student_performance.calculate_all()
    student.count_num_backlogs()


def update_subject_metrics(subjects, semester, section):
    """Update or create subject metrics."""
    for subject in subjects.values():
        subject_metrics, _ = SubjectMetrics.objects.get_or_create(
            subject=subject, semester=semester, section=section
        )
        subject_metrics.calculate_metrics()


def update_semester_metrics(semester, section):
    """Update or create semester metrics."""
    semester_metrics, _ = SemesterMetrics.objects.get_or_create(
        semester=semester, section=section
    )
    semester_metrics.calculate_metrics()


def batch_add_scores(student, semester, scores, subjects, existing_scores):
    """Main function to batch add scores."""
    try:
        marks_new = []
        marks_update = []

        # Process each score
        for s in scores:
            handle_score_update_or_create(
                s, subjects, student, existing_scores, marks_new, marks_update
            )

        # Perform bulk database operations
        process_scores(marks_new, marks_update)

        # Update student performance
        update_student_performance(student, semester)

    except Exception as e:
        raise Exception(
            f"Failed to process scores for student {student.id}: {str(e)}"
        ) from e


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
