from generator import clean_context

def test_answer_that_is_only_a_cross_reference_leaves_no_dangling_arrow():
    assert clean_context("1. How do I register my business? \u2192 See 01.1.") == ""


def test_cross_reference_after_a_real_answer_keeps_the_answer():
    assert clean_context("2. Does DTI give capital? \u2192 No. See 04.1.") == \
        "2. Does DTI give capital? \u2192 No."


def test_removing_a_section_reference_leaves_no_double_space():
    assert clean_context("DTI business name fees (01.2) apply only to sole proprietorships.") == \
        "DTI business name fees apply only to sole proprietorships."


def test_status_line_is_removed():
    assert clean_context("Fee is \u20b1200.\n(Status: VERIFIED)") == "Fee is \u20b1200."