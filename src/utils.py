def file_size(path):
    size  = path.stat().st_size
    units = ["B", "KB", "MB", "GB"]

    unit = 0
    while size > 1024:
        size /= 1024
        unit += 1

    return f"{size:.1f}{units[unit]}"    