import re

import nerodia


def error_403(selenium):
  browser = nerodia.browser.Browser(browser=selenium)
  return browser.h1(visible_text="Forbidden")


def error_404(selenium):
  browser = nerodia.browser.Browser(browser=selenium)
  return browser.body(visible_text=re.compile("not found"))
