import re


ERROR_PATTERNS = {
    "Database/Transaction": [
        r"STATUS_MARKED_ROLLBACK",
        r"RollbackException",
        r"deadlock",
        r"ORA-\d+",
        r"SQLSyntaxErrorException",
        r"datasource"
    ],

    "Timeout": [
        r"TimeoutException",
        r"Read timed out",
        r"SocketTimeoutException",
        r"timed out"
    ],

    "Security": [
        r"SSLHandshakeException",
        r"certificate",
        r"PKIX path building failed",
        r"AccessDenied"
    ],

    "Authentication": [
        r"401 Unauthorized",
        r"invalid credentials",
        r"authentication failed",
        r"login failed"
    ],

    "Network": [
        r"Connection refused",
        r"UnknownHostException",
        r"connection reset",
        r"network unreachable"
    ],

    "Application": [
        r"NullPointerException",
        r"IndexOutOfBoundsException",
        r"IllegalArgumentException",
        r"ClassCastException"
    ],

    "Infrastructure": [
        r"OutOfMemoryError",
        r"disk full",
        r"CPU",
        r"memory leak"
    ]
}


def classify_incident(text):
    text_lower = text.lower()

    matches = []
    # Buscar patrones en el texto y clasificar según la primera categoría coincidente
    for category, patterns in ERROR_PATTERNS.items():
        for pattern in patterns:
            # Usar búsqueda de expresiones regulares para encontrar coincidencias
            if re.search(pattern.lower(), text_lower): # Convertir el patrón a minúsculas para la comparación
                matches.append(category)
                break

    if not matches:
        return "Unknown"

    return matches[0]