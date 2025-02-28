def parse_time(time_str):
    """Parse a time string in HH:MM format to a time object"""
    hours, minutes = map(int, time_str.split(":"))
    return time(hour=hours, minute=minutes)


def get_formatted_blocks(blocks, all_blocks, session_dates=None):
    """Convert time blocks to formatted strings, with blanks for occupied times"""
    formatted = []

    # Convert blocks to comparable format
    blocks_set = {
        (parse_time(start).time(), parse_time(end).time()) for start, end in blocks
    }

    for block in all_blocks:
        if any(is_conflict(block, class_block) for class_block in blocks_set):
            # Room is occupied - show blank space
            formatted.append(" " * 11)  # Same width as "HH:MM-HH:MM"
        else:
            # Room is vacant - show the time
            formatted.append(
                f"{block[0].strftime('%H:%M')}-{block[1].strftime('%H:%M')}"
            )
        formatted.append("   ")  # Add 3 spaces of padding between blocks

    # Remove the trailing padding from the last block
    if formatted:
        formatted.pop()

    return formatted


def check_overlaps(blocks, session_dates=None):
    if not session_dates:
        return blocks

    for block in blocks:
        print(f"Checking block {block} against session dates {session_dates}")
        # Logic to check overlaps

    return blocks
