TERM_SESSION_DATES = {
    # (Term, Session): (Start Date, End Date)
    (20251, 1): ("2024-08-16", "2024-12-10"),
    (20251, 2): ("2024-08-16", "2024-10-08"),
    (20251, 3): ("2024-09-04", "2024-11-26"),
    (20251, 4): ("2024-10-14", "2024-12-10"),
    (20252, 1): ("2025-01-06", "2025-05-04"),
    (20252, 2): ("2025-01-06", "2025-03-02"),
    (20252, 3): ("2025-01-22", "2025-04-18"),
    (20252, 4): ("2025-03-13", "2025-05-04"),
    (20253, 1): ("2025-05-13", "2025-08-05"),
    (20253, 2): ("2025-05-13", "2025-06-23"),
    (20253, 3): ("2025-06-26", "2025-08-05"),
}


def get_dates(term, session):
    """
    Look up the start and end dates for a given term and session.

    :param term: The term code (integer)
    :param session: The session number (integer)
    :return: A tuple of (start_date, end_date) or (None, None) if not found
    """

    # Convert term and session to integers if they're not already
    try:
        term = int(term)
        session = int(session)
    except ValueError:
        # print(f"Debug: Could not convert Term or Session to int")
        return (None, None)
    result = TERM_SESSION_DATES.get((term, session), (None, None))
    return result
