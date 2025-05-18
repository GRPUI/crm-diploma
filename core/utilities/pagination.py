def paginate(items: list, page: int, page_size: int) -> dict:
    next_page = len(items) > page_size
    return {"page": page, "next_page": next_page, "items": items[:page_size]}
