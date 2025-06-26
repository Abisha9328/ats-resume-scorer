def parse_job_description(text: str) -> str:
    return text.strip().replace('\n', ' ').replace('\r', '')
