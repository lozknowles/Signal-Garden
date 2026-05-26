COMMERCIAL_MOBILE_RETAIL_DOMAINS = {
    "tescomobile.com",
    "ee.co.uk",
    "vodafone.co.uk",
    "o2.co.uk",
    "three.co.uk",
    "giffgaff.com",
    "carphonewarehouse.com",
    "phones.co.uk",
    "mobiles.co.uk",
    "uswitch.com",
    "moneysupermarket.com",
}

COMMERCIAL_MOBILE_RETAIL_TITLE_MARKERS = [
    "sim only",
    "phone contract",
    "phone contracts",
    "mobile phones",
    "mobile phone deals",
    "sim deals",
    "pay monthly phones",
    "upgrade deals",
]


def is_commercial_mobile_retail_source(record):
    """Return True for carrier/retail pages that are not research sources."""
    domain = (record.get("domain", "") or "").lower()
    title_blob = " ".join(
        str(
            record.get(key, "") or ""
        )
        for key in [
            "title",
            "full_title",
            "note_title",
            "description",
        ]
    ).lower()

    if any(pattern in domain for pattern in COMMERCIAL_MOBILE_RETAIL_DOMAINS):
        return True

    return any(
        marker in title_blob
        for marker in COMMERCIAL_MOBILE_RETAIL_TITLE_MARKERS
    )


def source_rejection_reason(record):
    """Explain why a source should stay out of research-facing outputs."""
    if is_commercial_mobile_retail_source(record):
        return "commercial-mobile-retail"

    return ""
