def get_group_name(unqiue_id) -> str:
    """
    Returns a group name. `unique_id` is a value that will be converted to `str`, one
    that uniquely represents the group.
    """
    return f"chat_{str(unqiue_id)}"


def get_channel_group_name(unqiue_id) -> str:
    """
    Returns the group name that is used to uniquely identify a channel. `unique_id` is
    a value that will be converted to `str`, one that uniquely represents the channel.
    """
    return f"user_{str(unqiue_id)}"
