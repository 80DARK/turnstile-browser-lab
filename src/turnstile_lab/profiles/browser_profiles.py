import random
from typing import Optional


class BrowserConfig:
    SEC_CH_UA_CONFIGS = {
        "chrome": {
            "139": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
            "138": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
            "137": "\"Google Chrome\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
            "136": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
        },
        "edge": {
            "139": "\"Not;A=Brand\";v=\"99\", \"Microsoft Edge\";v=\"139\", \"Chromium\";v=\"139\"",
            "138": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\"",
            "137": "\"Microsoft Edge\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
        },
        "avast": {
            "138": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Avast Secure Browser\";v=\"138\"",
            "137": "\"Avast Secure Browser\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
        },
        "brave": {
            "139": "\"Not;A=Brand\";v=\"99\", \"Brave\";v=\"139\", \"Chromium\";v=\"139\"",
            "138": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Brave\";v=\"138\"",
            "137": "\"Brave\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
        },
    }

    USER_AGENT_CONFIGS = {
        "chrome": {
            "139": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "138": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "137": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "136": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        },
        "edge": {
            "139": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
            "138": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "137": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        },
        "avast": {
            "138": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Avast/138.0.0.0",
            "137": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Avast/137.0.0.0",
        },
        "brave": {
            "139": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "138": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "137": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        },
    }

    def __init__(self):
        self.available_browsers = list(self.USER_AGENT_CONFIGS.keys())

    def get_random_browser_config(self, browser_type: Optional[str] = None):
        if browser_type in ["chrome", "chromium", "msedge", "avast"]:
            chromium_browsers = ["chrome", "edge", "avast", "brave"]
            browser = random.choice(chromium_browsers)
        elif browser_type == "camoufox":
            return "firefox", "custom", "", ""
        else:
            browser = random.choice(self.available_browsers)

        versions = list(self.USER_AGENT_CONFIGS[browser].keys())
        version = random.choice(versions)
        user_agent = self.USER_AGENT_CONFIGS[browser][version]
        sec_ch_ua = self.SEC_CH_UA_CONFIGS.get(browser, {}).get(version, "")
        return browser, version, user_agent, sec_ch_ua

    def get_browser_config(self, browser: str, version: str):
        try:
            user_agent = self.USER_AGENT_CONFIGS[browser][version]
            sec_ch_ua = self.SEC_CH_UA_CONFIGS.get(browser, {}).get(version, "")
            return user_agent, sec_ch_ua
        except KeyError:
            return None


browser_config = BrowserConfig()