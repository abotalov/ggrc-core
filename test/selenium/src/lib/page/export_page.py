# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Export page with Export Panels."""

import os

from lib import base
from lib.constants import locator, element
from lib.utils import selenium_utils, test_utils


class ExportItem(base.Component):
  """Export item on Export Page."""
  _locators = locator.ExportItem

  def __init__(self, driver, export_item_elem):
    super(ExportItem, self).__init__(driver)
    self.export_item_elem = export_item_elem

  def download_csv(self):
    base.Button(self.export_item_elem,
                self._locators.DOWNLOAD_CSV_XPATH).click()


class ExportPage(base.AbstractPage):
  """Export Page."""
  _locators = locator.ExportPage
  _elements = element.ExportPage

  def __init__(self, driver):
    super(ExportPage, self).__init__(driver)
    self.export_page = self._driver.find_element(
        *self._locators.EXPORT_PAGE_CSS)
    self.add_obj_type_btn = base.Button(
        self.export_page, self._locators.ADD_OBJECT_TYPE_BTN_XPATH)
    self.export_objs_btn = base.Button(
        self.export_page, self._locators.EXPORT_OBJECTS_BTN_CSS)

  def get_export_items(self):
    """Get the list of all Export Items which are present on Export Page."""
    return [ExportItem(self._driver, export_item_elem) for export_item_elem in
            self.export_page.find_elements(*self._locators.EXPORT_ITEM_CSS)]

  def export_objs_to_csv(self, path_to_export_dir):
    """Click to 'Export Objects' button to export objects, wait for export,
    download as CSV and return path to the downloaded file.
    """
    export_items_before_count = len(self.get_export_items())
    self.export_objs_btn.click()

    def exported_item():
      """Return the export item that was just created."""
      difference = len(self.get_export_items()) - export_items_before_count
      if difference == 1:
        return self.get_export_items()[-1]
      return None
    export_item = test_utils.wait_for(exported_item)
    selenium_utils.set_chrome_download_location(
        self._driver, path_to_export_dir)
    downloads_before = os.listdir(path_to_export_dir)
    export_item.download_csv()

    def path_to_downloaded_file():
      """Path to a file that has appeared."""
      difference = set(os.listdir(path_to_export_dir)) - set(downloads_before)
      if len(difference) == 1:
        filename = list(difference)[0]
        return os.path.join(path_to_export_dir, filename)
      return None
    return test_utils.wait_for(path_to_downloaded_file)
