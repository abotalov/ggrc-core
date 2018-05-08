from selenium.common.exceptions import WebDriverException

from lib.constants import objects, users
from lib.service import webui_service, rest_service, webui_errors
from lib.utils import selenium_utils


def create_program(selenium):
  return webui_service.ProgramsService(selenium).create_obj()


def create_control(selenium):
  return webui_service.ControlsService(selenium).create_obj()


def assert_can_view(selenium, obj, can_view):
  try:
    ui_obj = _get_ui_service(selenium, obj).get_obj_from_info_page(obj)
  except WebDriverException:
    assert webui_errors.error_403(selenium).exists
    assert not can_view
    return
  a = 1
  # assert ui_obj == obj.repr_ui()


def assert_can_edit(selenium, obj, can_edit):
  ui_service = _get_ui_service(selenium, obj=obj)
  info_page = ui_service.open_info_page_of_obj(obj)
  els_shown_for_editor = info_page.els_shown_for_editor()
  assert [item.exists for item in els_shown_for_editor] == \
         [can_edit] * len(els_shown_for_editor)
  assert info_page.info_3bbs_btn.exists == can_edit
  if can_edit:
    _assert_title_editable(obj, ui_service, info_page)


def assert_can_delete(selenium, obj, can_delete):
  info_page = _get_ui_service(selenium, obj=obj).open_info_page_of_obj(obj)
  assert info_page.info_3bbs_btn.exists == can_delete
  if can_delete:
    info_page.open_info_3bbs().select_delete().confirm_delete()
    selenium_utils.open_url(selenium, obj.url)
    assert webui_errors.error_404(selenium).exists


def _get_ui_service(selenium, obj=None, obj_type=None):
  if not obj_type:
    obj_type = objects.get_plural(obj.type)
  return webui_service.BaseWebUiService(selenium, obj_type)


def _assert_title_editable(obj, ui_service, info_page):
  new_title = "[EDITED]" + obj.title
  info_page.open_info_3bbs().select_edit().edit_minimal_data(
      title=new_title).save_and_close()
  obj.update_attrs(title=new_title, modified_by=users.current_user_email(),
      updated_at=rest_service.ObjectsInfoService().get_obj(
          obj=obj).updated_at).repr_ui()
  new_ui_obj = ui_service.get_obj_from_info_page(obj)
  assert new_ui_obj == obj.repr_ui()
