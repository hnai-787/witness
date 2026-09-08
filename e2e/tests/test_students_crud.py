import uuid

from e2e_tests.pages.student_form_page import StudentFormPage


def _unique_email() -> str:
    return f"e2e-{uuid.uuid4().hex[:10]}@example.com"


def test_admin_can_create_a_student(admin_dashboard):
    email = _unique_email()
    admin_dashboard.add_student("Edsger", "Dijkstra", 60, "Rotterdam", email)

    assert admin_dashboard.alerts.has_message_containing("added successfully")
    row = admin_dashboard.find_row_by_email(email)
    assert row is not None
    assert row.fname == "Edsger"
    assert row.lname == "Dijkstra"


def test_admin_can_edit_a_student(admin_dashboard, base_url, driver):
    email = _unique_email()
    admin_dashboard.add_student("Donald", "Knuth", 70, "Stanford", email)
    row = admin_dashboard.find_row_by_email(email)
    student_id = row.student_id

    form = StudentFormPage.open(driver, base_url, student_id)
    assert form.field_value("fname") == "Donald"
    form.set_field("city", "PaloAlto")
    dashboard = form.submit()

    assert dashboard.alerts.has_message_containing("updated successfully")
    updated_row = dashboard.find_row_by_email(email)
    assert updated_row.city == "PaloAlto"


def test_admin_can_delete_a_student(admin_dashboard):
    email = _unique_email()
    admin_dashboard.add_student("Grace", "Test", 33, "Testville", email)
    row = admin_dashboard.find_row_by_email(email)
    assert row is not None

    row.click_delete()
    admin_dashboard.wait().until(lambda d: admin_dashboard.alerts.has_message_containing("deleted"))

    assert admin_dashboard.find_row_by_email(email) is None


def test_staff_can_create_a_student_but_not_delete_it(staff_dashboard):
    """Staff has CREATE_STUDENT but not DELETE_STUDENT (Project #7's
    permission matrix) -- both halves are visible in one browser flow.
    """
    email = _unique_email()
    staff_dashboard.add_student("Ada", "Test", 29, "Testville", email)
    row = staff_dashboard.find_row_by_email(email)
    assert row is not None
    assert row.has_edit_action()
    assert not row.has_delete_action()
