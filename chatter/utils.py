def get_group_name(unqiue_id: str) -> str:
    """
    Returns a group name. `unique_id` is a string that uniquely represents
    the group.
    """
    return f"chat_{unqiue_id}"
