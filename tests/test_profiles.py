from turnstile_lab.profiles.browser_profiles import BrowserConfig


def test_get_browser_config_valid():
    config = BrowserConfig()

    result = config.get_browser_config("chrome", "139")

    assert result is not None
    useragent, sec_ch_ua = result
    assert "Chrome/139.0.0.0" in useragent
    assert "Google Chrome" in sec_ch_ua or "Chromium" in sec_ch_ua


def test_get_browser_config_invalid():
    config = BrowserConfig()

    result = config.get_browser_config("chrome", "999")

    assert result is None


def test_get_random_browser_config_chromium_family():
    config = BrowserConfig()

    browser, version, useragent, sec_ch_ua = config.get_random_browser_config("chromium")

    assert browser in {"chrome", "edge", "avast", "brave"}
    assert version
    assert useragent
    assert isinstance(sec_ch_ua, str)


def test_get_random_browser_config_camoufox():
    config = BrowserConfig()

    browser, version, useragent, sec_ch_ua = config.get_random_browser_config("camoufox")

    assert browser == "firefox"
    assert version == "custom"
    assert useragent == ""
    assert sec_ch_ua == ""