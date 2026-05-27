"""
Tests for the basic content of the index.html file of a personal web site.

Requires Selenium 4.6+ (uses Selenium Manager to auto-manage chromedriver)
and a recent installation of Google Chrome.
"""

import json
import pytest
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def _build_url(site_url, page=""):
  base = site_url.rstrip("/")
  if not page:
    return base + "/"
  return base + "/" + page.lstrip("/")


class Tests:

  @pytest.fixture(scope="class")
  def settings(self):
    with open('./settings.json', 'r') as f:
      yield json.load(f)

  @pytest.fixture(scope="class")
  def driver(self, settings):
    options = Options()
    options.add_argument("--window-size=1400,1000")
    driver = webdriver.Chrome(options=options)
    driver.get(_build_url(settings["site_url"]))
    yield driver
    driver.quit()

  def test_title(self, driver, settings):
    """The page title must include the student's name."""
    assert settings["name"] in driver.title

  def test_h1(self, driver, settings):
    """There must be an h1 element containing the student's name."""
    elem = driver.find_element(By.TAG_NAME, "h1")
    assert settings["name"] in elem.text

  def test_ol_exists(self, driver, settings):
    """There must be an ordered list of assignment links with at least 2 items."""
    elems = driver.find_elements(By.CSS_SELECTOR, "ol li")
    assert len(elems) >= 2

  def test_ol_has_all_assignments(self, driver, settings):
    """The ordered list must contain at least one item per required assignment link."""
    target_urls = [
      'about_me.html',
      'topic_of_interest.html',
      'user_experience_design.html',
      'professional_site.html',
      'photoshop.html',
      'vector_graphics.html',
      'animated_gif.html',
      'video.html',
    ]
    li_html = " ".join(
      (li.get_attribute("innerHTML") or "")
      for li in driver.find_elements(By.CSS_SELECTOR, "ol li")
    )
    for url in target_urls:
      assert url in li_html, (
        "Ordered list is missing a list item that links to {}".format(url)
      )

  def test_link_href_exists(self, driver):
    """The page must link to each of the assignment pages by file name."""
    target_urls = [
      'index.html',
      'about_me.html',
      'topic_of_interest.html',
      'user_experience_design.html',
      'professional_site.html',
      'animated_gif.html',
      'video.html',
    ]
    for url in target_urls:
      try:
        elem = driver.find_element(
          By.CSS_SELECTOR, "a[href='{0}'], a[href$='/{0}']".format(url)
        )
      except NoSuchElementException:
        elem = None
      assert elem, "Missing link with href ending in '{}'".format(url)

  def test_link_text_exists(self, driver):
    """The page must mention each required assignment by name in its links."""
    target_terms = [
      'UNIX', 'HTML', 'CSS', 'JQuery', 'User Experience',
      'Responsive Design', 'Bootstrap', 'Photoshop', 'Vector Graphics',
      'Animated GIF', 'Digital Video',
    ]
    elems_text = ''.join(
      x.text.strip().lower().replace('assignment', '')
      for x in driver.find_elements(By.CSS_SELECTOR, "a")
    )
    for term in target_terms:
      assert term.lower() in elems_text, (
        "No link text mentions '{}'.".format(term)
      )

  def test_doctype_present(self, driver):
    """The page must declare an HTML5 doctype."""
    doctype = driver.execute_script(
      "return document.doctype ? document.doctype.name : null;"
    )
    assert doctype and doctype.lower() == "html"

  def test_lang_attribute(self, driver):
    """The html element must declare a lang attribute."""
    html = driver.find_element(By.TAG_NAME, "html")
    assert (html.get_attribute("lang") or "").strip() != ""
