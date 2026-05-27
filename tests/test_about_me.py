"""
Tests for the basic content of the about_me.html file.

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
    driver.get(_build_url(settings["site_url"], "about_me.html"))
    yield driver
    driver.quit()

  def test_h1_exists(self, driver):
    """The page must include an h1."""
    elem = driver.find_element(By.TAG_NAME, "h1")
    assert elem.text.strip() != ""

  def test_two_sections(self, driver):
    """Two distinct <section> elements must exist."""
    elems = driver.find_elements(By.TAG_NAME, "section")
    assert len(elems) >= 2

  def test_two_headings(self, driver):
    """Each required section must have a nested h2 with the exact heading text."""
    elems = driver.find_elements(By.CSS_SELECTOR, "section h2")
    assert len(elems) >= 2

    found_background = False
    found_interests = False
    for elem in elems:
      heading = elem.text.strip().lower()
      if heading == "my background":
        found_background = True
      elif heading == "my interests":
        found_interests = True
    assert found_background, (
      'Did not find a <section> containing <h2>My Background</h2>.'
    )
    assert found_interests, (
      'Did not find a <section> containing <h2>My Interests</h2>.'
    )

  def test_paragraph_in_each_section(self, driver):
    """Each <section> must include at least one <p> with text."""
    sections = driver.find_elements(By.TAG_NAME, "section")
    for s in sections[:2]:
      ps = s.find_elements(By.TAG_NAME, "p")
      assert any((p.text or "").strip() for p in ps), (
        "A required <section> has no <p> with text content."
      )

  def test_two_images(self, driver):
    """At least two <img> elements must be present."""
    elems = driver.find_elements(By.TAG_NAME, "img")
    assert len(elems) >= 2

  def test_images_have_alt(self, driver):
    """Every <img> must have a non-empty alt attribute for accessibility."""
    elems = driver.find_elements(By.TAG_NAME, "img")
    for img in elems:
      alt = img.get_attribute("alt")
      assert alt is not None and alt.strip() != "", (
        "An <img> element is missing an alt attribute: {}".format(
          img.get_attribute("src")
        )
      )

  def test_relative_link_to_index(self, driver):
    """Must include a relative link back to index.html (not an absolute URL)."""
    try:
      a = driver.find_element(By.CSS_SELECTOR, "a[href='index.html']")
    except NoSuchElementException:
      a = None
    assert a, "No relative <a href='index.html'> found on the page."

  def test_relative_link_to_more_about_me(self, driver):
    """Must include a relative link to more_about_me.html."""
    try:
      a = driver.find_element(By.CSS_SELECTOR, "a[href='more_about_me.html']")
    except NoSuchElementException:
      a = None
    assert a, "No relative <a href='more_about_me.html'> found on the page."

  def test_absolute_external_link(self, driver, settings):
    """At least one absolute link must lead to a different web site."""
    own_host = urlparse(settings["site_url"]).netloc
    found = False
    for a in driver.find_elements(By.TAG_NAME, "a"):
      href = a.get_attribute("href") or ""
      parsed = urlparse(href)
      if parsed.scheme in ("http", "https") and parsed.netloc and parsed.netloc != own_host:
        found = True
        break
    assert found, (
      "No absolute link to an external web site was found on about_me.html."
    )
