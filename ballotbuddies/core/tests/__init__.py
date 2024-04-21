import log


def decode(response, verbose=True) -> str:
    html = response.content.decode().strip()
    message = f"{response.status_code} response"
    if verbose:
        message += f"\n\n{html}\n\n"
    log.info(f"{response.status_code} response")
    return html
