def test_search_finds_a_known_seeded_student(admin_dashboard):
    admin_dashboard.search("Hampton")  # unique to Katherine Johnson in seed_e2e.py
    rows = admin_dashboard.student_rows()
    assert len(rows) == 1
    assert rows[0].lname == "Johnson"


def test_search_with_no_matches_shows_empty_state(admin_dashboard):
    admin_dashboard.search("no-student-anywhere-matches-this-string")
    assert admin_dashboard.student_rows() == []
    assert "No students found" in admin_dashboard.driver.page_source


def test_literal_percent_in_search_is_not_treated_as_a_wildcard(admin_dashboard):
    """Real-browser confirmation of the icontains(autoescape=True)
    behavior Rollkeeper's own pytest suite already covers at the HTTP
    layer -- here confirming what an actual user typing "%" and expecting
    literal-character behavior actually sees rendered.
    """
    admin_dashboard.search("%")
    assert admin_dashboard.student_rows() == []
