from app import format_answer


def test_markdown_bullets_and_bold_become_html_list():
    assert format_answer("You need:\n*   Barangay clearance\n* **Police** clearance") == \
        "You need:\n<ul><li>Barangay clearance</li><li><strong>Police</strong> clearance</li></ul>"


def test_html_in_answer_is_escaped():
    assert format_answer("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
