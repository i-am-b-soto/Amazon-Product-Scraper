async def get_new_proxy(proxy_info):
    """
        return dict
    """
    proxy_url = await proxy_info.new_url()
    parsed = urlparse(proxy_url)
    return {
        "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
        "username": parsed.username,
        "password": parsed.password,
    }


async def get_new_browser(pw, proxy_info):
    """

    """
    (proxy_server, proxy_username, proxy_password) = await get_new_proxy(proxy_info)
    #browser = await pw.chromium.launch(headless=False, proxy=get_new_proxy(proxy_info))
    browser = await pw.chromium.launch(headless=False)
    return browser
