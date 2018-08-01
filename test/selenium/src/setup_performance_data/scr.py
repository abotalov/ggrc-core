import collections
import csv
import datetime
import fractions
import itertools
import math
import os
import re
import tempfile
import time

from nerodia import browser
from nerodia.wait.wait import TimeoutError

from lib import environment, url, users
from lib.constants import objects
from lib.decorator import memoize
from lib.service import rest_facade
from lib.utils import string_utils, selenium_utils, file_utils

gmail_email = os.environ["LOGIN_EMAIL"]
gmail_password = os.environ["LOGIN_PASSWORD"]
download_username = os.environ["DOWNLOAD_USERNAME"]

br = browser.Browser()


def gmail_login():
  br.text_field(aria_label="Email or phone").set(gmail_email)
  br.element(id="identifierNext").click()
  time.sleep(1.5)  # wait for password elements to have correct position
  br.text_field(aria_label="Enter your password").set(gmail_password)
  br.element(id="passwordNext").click()
  # needed only once
  # br.link(text="Advanced").click()
  # br.link(text="Go to GGRC Dev (unsafe)").click()
  # br.element(text="ALLOW").click()


current_user = users._current_user = users.FakeSuperUser()
br.goto(url.Urls().gae_login(current_user))
users.set_current_logged_in_user(users.UI_USER, users.current_user())
br.goto("{}import".format(environment.app_url))
br.element(class_name="release-notes").button(text="Close").click()


class ImportPage(object):
  def choose_file(self, csv_file):
    br.goto("{}import".format(environment.app_url))
    br.element(class_name="import-buttons").wait_for_present()
    selenium_utils.wait_for_js_to_load(br.driver)
    time.sleep(4)

    def click_choose_file_to_import():
      br.element(class_name="spinner-icon").wait_until_not_present()
      btns = [br.button(text="Choose file to import"),
              br.button(text="Choose new file to import")]
      for btn in btns:
        if btn.present:
          btn.click()
          return True
      return False

    txt_auth = "Authorize Google API"
    txt_sign = "Sign in - Google Accounts"
    diag_frame = "picker-dialog-frame"

    from lib.utils import test_utils
    test_utils.wait_for(click_choose_file_to_import)
    br.link(text=txt_auth).click()
    time.sleep(2)
    if len(br.windows()) > 1:
      br.window(title=txt_sign).use()
      gmail_login()
      br.windows()[0].use()
      time.sleep(4)
      iframe = br.iframe(class_name=diag_frame)
      iframe.file_field(type="file").set(csv_file.name)
      br.link(text=txt_auth).click()
      br.window(title=txt_sign).use()
      br.element(text=gmail_email).click()
      br.windows()[0].use()
    else:
      iframe = br.iframe(class_name=diag_frame)
      iframe.file_field(type="file").set(csv_file.name)
    return self

  def import_file(self):
    time.sleep(0.5)
    confirm_text = "I confirm, that data being imported is " \
                   "complete and accurate."
    br.label(text=confirm_text).click()
    br.button(text="Proceed").click()
    # App sends AJAX checks frequently only during the few first dozen seconds
    for i in xrange(0, 20):
      try:
        br.button(text="Choose file to import").wait_until_present(timeout=12)
      except TimeoutError:
        br.refresh()
        if br.element(text="503 - This request has timed out.").present:
          # There is currently a bug on localhost:
          # When import is started, dev server becomes unavailable until
          # it becomes finished. So we refresh page until it becomes available.
          continue
        selenium_utils.wait_for_js_to_load(br.driver)
        time.sleep(4)
        br.element(class_name="spinner-icon").wait_until_not_present()
        continue
      break
    return self


def prepare_csv_rows(obj_name, number, part_of_name, columns):
  rows = []
  for i in xrange(number):
    new_columns = []
    for column_name, column_value in columns:
      if isinstance(column_value, collections.Iterator):
        column_value = next(column_value)
      new_columns.append((column_name, column_value))
    rows.append(collections.OrderedDict([
      (obj_name, ""),
      ("Code", ""),
      ("Title", obj_name + " {} {}".format(part_of_name, i))] + new_columns))
  return rows


def prepare_programs(number, part_of_name):
  # columns = [
  #   ("Program Managers", next_users(100)),
  #   ("Program Editors", next_users(50)),
  #   ("Program Readers", next_users(600))]
  columns = [
    ("Program Managers", "user@example.com")
  ]
  return prepare_csv_rows("Program", number, part_of_name, columns)


def prepare_audits(number, part_of_name, add_cols):
  columns = [
    ("Audit Captains", "user@example.com"),
    ("State", "Planned")
  ] + add_cols
  return prepare_csv_rows("Audit", number, part_of_name, columns)


def prepare_firstclass_objs(obj_type, number, part_of_name, add_cols=None):
  """Method create 1st class pbjects"""
  columns = [("Admin", "user@example.com")]
  if add_cols is not None:
    columns.extend(add_cols)

  return prepare_csv_rows(
    objects.transform_to("s", obj_type), number, part_of_name, columns)


def prepare_objectives(number, part_of_name, additional_columns):
  # columns = [
  #   ("Admin", next_users(30)),
  #   ("Primary Contacts", next_users(10)),
  #   ("Secondary Contacts", next_users(10))] + additional_columns
  columns = [
    ("Admin", "user@example.com")
  ] + additional_columns
  return prepare_csv_rows("Objective", number, part_of_name, columns)


def prepare_controls(number, part_of_name, additional_columns):
  # columns = [
  #   ("Admin", next_users(30)),
  #   ("Primary Contacts", next_users(10)),
  #   ("Secondary Contacts", next_users(10))] + additional_columns
  columns = [
    ("Admin", "user@example.com")
  ] + additional_columns
  return prepare_csv_rows("Control", number, part_of_name, columns)


def prepare_standards(number, part_of_name, additional_columns):
  # columns = [
  #   ("Admin", next_users(30)),
  #   ("Primary Contacts", next_users(10)),
  #   ("Secondary Contacts", next_users(10))] + additional_columns
  columns = [
    ("Admin", "user@example.com")
  ] + additional_columns
  return prepare_csv_rows("Standard", number, part_of_name, columns)


def prepare_regulations(number, part_of_name, additional_columns):
  # columns = [
  #   ("Admin", next_users(30)),
  #   ("Primary Contacts", next_users(10)),
  #   ("Secondary Contacts", next_users(10))] + additional_columns
  columns = [
    ("Admin", "user@example.com")
  ] + additional_columns
  return prepare_csv_rows("Regulation", number, part_of_name, columns)


def prepare_clauses(number, part_of_name, additional_columns):
  # columns = [
  #   ("Admin", next_users(30)),
  #   ("Primary Contacts", next_users(10)),
  #   ("Secondary Contacts", next_users(10))] + additional_columns
  columns = [
    ("Admin", "user@example.com")
  ] + additional_columns
  return prepare_csv_rows("Clause", number, part_of_name, columns)


def write_file(csv_file, obj_dicts):
  writer = csv.writer(csv_file)
  first_dict = obj_dicts[0]
  writer.writerow(['Object type', [''] * (len(first_dict) - 1)])
  writer.writerow(first_dict.keys())
  for obj_dict in obj_dicts:
    writer.writerow(obj_dict.values())
  csv_file.seek(0)
  reader = csv.reader(csv_file)
  for row in reader:
    print row


@memoize
def users():
  directory = os.path.dirname(__file__)
  with open(os.path.join(directory, 'users.txt')) as f:
    content = f.readlines()
  return [email.strip() for email in content]


@memoize
def user_generator():
  return itertools.cycle(users())


def random_name():
  return string_utils.StringMethods.random_string() + str(
    datetime.datetime.now())


def next_items(iterable, n):
  return list(itertools.islice(iterable, n))


def next_users(n):
  return "\n".join(next_items(user_generator(), n))


def next_objs(iterable, n):
  code_generator = itertools.cycle(iterable)
  return itertools.islice(code_generator, n)


def import_obj(obj_type, number, add_cols=None):
  """Method create import object and return part of name."""
  with tempfile.NamedTemporaryFile(mode="r+", suffix=".csv") as tmp_file:
    part_of_name = string_utils.StringMethods.random_string()
    if objects.PROGRAMS == objects.transform_to("p", obj_type, False):
      ggrc_objs = prepare_programs(number, part_of_name)
    elif objects.AUDITS == objects.transform_to("p", obj_type, False):
      ggrc_objs = prepare_audits(number, part_of_name, add_cols)
    else:
      ggrc_objs = prepare_firstclass_objs(obj_type, number, part_of_name,
                                          add_cols)
    write_file(tmp_file, ggrc_objs)
    ImportPage().choose_file(tmp_file).import_file()
  return part_of_name


def export(obj_type, filer_query=None, **mapping_query):
  """Method export object code by provided query criteria."""

  # variables
  none_txt = "None"
  code_txt = "Code"
  btn_txt = "Download CSV"
  file_path_format = "/Users/{}/Downloads/{}"

  # open page
  br.goto("{}export".format(environment.app_url))
  br.element(class_name="export-buttons-wrap").wait_for_present()
  selenium_utils.wait_for_js_to_load(br.driver)

  # TODO check if any previous exports appear
  btn_trashes = br.elements(class_name="fa-trash-o")
  for btn in btn_trashes:
    btn.click()
    selenium_utils.wait_for_js_to_load(br.driver)

  # select object type
  br.select(class_name="option-type-selector").select(
    objects.transform_to("p", obj_type))
  selenium_utils.wait_for_js_to_load(br.driver)

  def deselect_items_in_panel(panel_name):
    """Method to deselect attr by clicking None."""
    panel = br.element(text=panel_name).parent(class_name="export-panel__group")
    panel.element(text=none_txt).click()
    return panel

  # select code attr to be exported only
  deselect_items_in_panel("Attributes").element(text=code_txt).click()
  deselect_items_in_panel("Mappings")

  # type filter if needed
  if filer_query:
    br.element(name="filter_query").send_keys(filer_query.strip())

  # select mapping for query
  if mapping_query:
    index = 0
    for key, value in mapping_query.items():
      br.element(class_name="add-filter-rule").click()
      selenium_utils.wait_for_js_to_load(br.driver)
      br.select(
        class_name="filter-type-selector select-filter{}".format(
          index)).select(objects.transform_to("s", key))
      br.element(name="filter_list.{}.filter".format(index)).send_keys(
        value.strip())
      index += 1

  # save csv
  br.element(id="export-csv-button").click()
  selenium_utils.wait_for_js_to_load(br.driver)
  export_item = br.element(class_name="current-exports__item")
  export_item.wait_until_present()
  file_name = export_item.text.split("\n")[0]
  export_item.element(text=btn_txt).click()

  # parse CSV file
  data = file_utils.get_list_objs_scopes_from_csv(
    path_to_csv=file_path_format.format(download_username, file_name))

  # convert list of dicts to list of str
  list_of_codes = [item[code_txt + "*"] for item in data[
    objects.transform_to("s", obj_type)]]
  return list_of_codes


def test_export_file():
  list1 = export("Controls", "ctrl", **{"Program":"PROGRAM-1213"})
  list2 = export("Control", "ctrl", **{"Programs": "PROGRAM-1213"})
  print list1 == list2


def write_file_and_import(tmp_file, objs):
  write_file(tmp_file, objs)
  import_page = ImportPage()
  import_page.choose_file(tmp_file)
  import_page.import_file()


def test_create_programs():
  with tempfile.NamedTemporaryFile(mode="r+", suffix=".csv") as tmp_file:
    part_of_name = string_utils.StringMethods.random_string()
    programs = prepare_programs(1, part_of_name=part_of_name)
    write_file_and_import(tmp_file, programs)
  program_code = export("Programs", part_of_name)[0]
  with tempfile.NamedTemporaryFile(mode="r+", suffix=".csv") as tmp_file:
    part_of_name = string_utils.StringMethods.random_string()
    additional_columns = [("map:program", program_code)]
    objectives = prepare_objectives(100, part_of_name, additional_columns)
    write_file_and_import(tmp_file, objectives)
  with tempfile.NamedTemporaryFile(mode="r+", suffix=".csv") as tmp_file:
    part_of_name = string_utils.StringMethods.random_string()
    additional_columns = [("map:program", program_code)]
    controls = prepare_controls(100, part_of_name, additional_columns)
    write_file_and_import(tmp_file, controls)


def test_create_users():
  people = rest_facade.create_objs("people", 1000, chunk_size=100)
  for person in people:
    print person.email


def split_with_repeat_iter(elements, n_parts_to_split):
  # Examples:
  # list_1 = [1, 2, 3, 4]
  # list(split_with_repeat_iter(list_1, 12))
  # => [[1], [1], [1], [2], [2], [2], [3], [3], [3], [4], [4], [4]]
  # list(split_with_repeat_iter(list_1, 2)) =>
  # => [[1, 2], [3, 4]]
  coeff = fractions.Fraction(len(elements)) / n_parts_to_split
  cur_pos = 0
  while cur_pos < len(elements):
    yield "\n".join(elements[int(cur_pos):int(math.ceil(cur_pos+coeff))])
    cur_pos += coeff


def import_and_export(obj_name, obj_count, add_cols=None):
  part_of_obj_name = import_obj(obj_name, obj_count, add_cols)
  return export(obj_name, part_of_obj_name)


def test_create_program_and_first_class_objs():
  stnd_count = 20
  requirement_count = 500
  clause_count = 50

  program_code = import_and_export(objects.PROGRAMS, 1)[0]

  map_to_program = [("map:program", program_code)]
  stnd_codes = import_and_export(objects.STANDARDS, stnd_count, map_to_program)

  mappings = [
    map_to_program[0],
    ("map:standard", split_with_repeat_iter(stnd_codes, requirement_count))]
  requirement_codes = import_and_export(
      objects.REQUIREMENTS, requirement_count, mappings)

  mappings = [
    map_to_program[0],
    ("map:requirement",
     split_with_repeat_iter(requirement_codes, clause_count))]
  clause_codes = import_and_export(objects.CLAUSES, clause_count, mappings)

  # stnd_codes = [
  #   "STANDARD - 11"
  #   , "STANDARD - 12"
  #   , "STANDARD - 13"
  #   , "STANDARD - 14"
  #   , "STANDARD - 15"
  #   , "STANDARD - 16"
  #   , "STANDARD - 17"
  #   , "STANDARD - 18"
  #   , "STANDARD - 19"
  #   , "STANDARD - 20"
  # ]
  # control
  # map_to_prg_stnd = [
  #   ("map:program", program_code),
  #   ("map:standard", next_objs(stnd_codes, ctrl_count / stnd_count))]
  # ctrl_name = import_obj(objects.CONTROLS, ctrl_count, map_to_prg_stnd)
  # ctrl_codes = export(objects.CONTROLS, ctrl_name)

  # assert len(ctrl_codes) == 10

  mappings = [("Program", program_code)]
  audit_code = import_and_export(objects.AUDITS, 1, mappings)[0]
