def pad(s: str, other: str) -> str:
    return "\n".join(other + line for line in s.splitlines())
