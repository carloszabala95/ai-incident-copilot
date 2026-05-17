def read_uploaded_file(uploaded_file):
    return uploaded_file.read().decode("utf-8", errors="ignore")


def get_file_preview(content, max_chars=2000):
    return content[:max_chars]