from selenium.common.exceptions import WebDriverException

from lib.constants import objects, users
from lib.service import webui_service, rest_service, webui_errors
from lib.utils import selenium_utils


def assert_can_view(selenium, obj, can_view):
  try:
    ui_obj = _get_ui_service(selenium, obj).get_obj_from_info_page(obj)
  except WebDriverException:
    assert not can_view
    assert webui_errors.error_403(selenium).exists
    return
  assert ui_obj == obj.repr_ui()


def assert_can_edit(selenium, obj, can_edit=True):
  ui_service = _get_ui_service(selenium, obj)
  info_page = ui_service.open_info_page_of_obj(obj)
  editable_items = info_page.items_for_editor()
  assert [item.exists for item in info_page.items_for_editor()] == \
         [can_edit] * len(editable_items)
  assert info_page.info_3bbs_btn.exists == can_edit
  if can_edit:
    _assert_title_editable(obj, ui_service, info_page)


def assert_can_delete(selenium, obj, can_edit):
  info_page = _get_ui_service(selenium, obj).open_info_page_of_obj(obj)
  assert info_page.info_3bbs_btn.exists == can_edit
  if can_edit:
    info_page.open_info_3bbs().select_delete().confirm_delete()
    selenium_utils.open_url(selenium, obj.url)
    assert webui_errors.error_404(selenium).exists


def _get_ui_service(selenium, obj):
  return webui_service.BaseWebUiService(selenium, objects.get_plural(obj.type))


def _assert_title_editable(obj, ui_service, info_page):
  new_title = "[EDITED]" + obj.title
  info_page.open_info_3bbs().select_edit().edit_minimal_data(
      title=new_title).save_and_close()
  obj.update_attrs(title=new_title, modified_by=users.current_user_email(),
      updated_at=rest_service.ObjectsInfoService().get_obj(
          obj=obj).updated_at).repr_ui()
  new_ui_obj = ui_service.get_obj_from_info_page(obj)
  assert new_ui_obj == obj.repr_ui()
