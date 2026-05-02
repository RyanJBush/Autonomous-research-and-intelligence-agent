from app.services.pii_redactor import PIIRedactor


def test_redact_clean_text_is_unchanged_with_zero_stats() -> None:
    redactor = PIIRedactor()
    text = "This article discusses climate policy and global governance."
    result, stats = redactor.redact(text)
    assert result == text
    assert stats == {"emails": 0, "phones": 0, "ssn": 0, "total": 0}


def test_redact_empty_string_returns_empty_with_zero_stats() -> None:
    result, stats = PIIRedactor().redact("")
    assert result == ""
    assert stats["total"] == 0


def test_redact_multiple_emails_counts_all_occurrences() -> None:
    redactor = PIIRedactor()
    text = "Contact alice@example.com and bob@test.org for more details."
    result, stats = redactor.redact(text)
    assert result.count("[REDACTED_EMAIL]") == 2
    assert stats["emails"] == 2
    assert stats["phones"] == 0
    assert stats["total"] == 2


def test_redact_multiple_phones_counts_all_occurrences() -> None:
    redactor = PIIRedactor()
    text = "Call 555-111-2222 or 800-333-4444 for support."
    result, stats = redactor.redact(text)
    assert result.count("[REDACTED_PHONE]") == 2
    assert stats["phones"] == 2
    assert stats["emails"] == 0
    assert stats["total"] == 2


def test_redact_ssn_only_leaves_other_fields_zero() -> None:
    redactor = PIIRedactor()
    result, stats = redactor.redact("Patient SSN: 123-45-6789.")
    assert "[REDACTED_SSN]" in result
    assert stats["ssn"] == 1
    assert stats["emails"] == 0
    assert stats["phones"] == 0
    assert stats["total"] == 1


def test_redact_preserves_non_pii_text_around_redacted_tokens() -> None:
    redactor = PIIRedactor()
    result, _ = redactor.redact("Reach out to admin@corp.io for access.")
    assert result.startswith("Reach out to ")
    assert result.endswith(" for access.")
    assert "[REDACTED_EMAIL]" in result
