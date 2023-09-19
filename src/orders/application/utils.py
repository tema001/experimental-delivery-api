
def check_new_events(events: list, cache: list | None) -> list:
    if cache is None or len(cache) == 0:
        return events

    return [ev for ev in events if ev not in cache]
