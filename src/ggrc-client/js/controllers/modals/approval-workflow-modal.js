/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import ModalsController from './modals_controller';
import {BUTTON_VIEW_SAVE_CANCEL} from '../../plugins/utils/modals';
import {getRole} from '../../plugins/utils/acl-utils';
import {REFRESH_APPROVAL} from '../../events/eventTypes';

let ApprovalWorkflowErrors = function () {
  let errors = null;
  if (!this.attr('contact')) {
    errors = {
      contact: 'Must be defined',
    };
  }
  if (!this.attr('end_date')) {
    errors = $.extend(errors, {
      end_date: 'Must be defined',
    });
  }
  return errors;
};

let ApprovalWorkflow = can.Observe({
  defaults: {
    original_object: null,
  },
}, {
  save: function () {
    let that = this;
    let aws_dfd = this.original_object.get_binding('approval_workflows').refresh_list();
    let reviewTemplate = _.template('Object review for ${type} "${title}"');
    let notifyTemplate = _.template('<br/><br/> ${name} (${email}) asked ' +
      'you to review newly created ${type} "${title}" before ${before}. ' +
      'Click <a href="${href}#workflows">here</a> to perform a review.'
    );
    let assigneeRole = getRole('TaskGroupTask', 'Task Assignees');
    let wfAdminRole = getRole('Workflow', 'Admin');

    return aws_dfd.then(function (aws) {
      const createDefaultTaskGroup = false;
      let ret;
      let user = GGRC.current_user;
      if (aws.length < 1) {
        ret = $.when(
          new CMS.Models.Workflow({
            access_control_list: [{
              ac_role_id: wfAdminRole.id,
              person: {
                id: user.id,
                type: 'Person',
              },
            }],
            unit: null,
            status: 'Active',
            title: reviewTemplate({
              type: that.original_object.constructor.title_singular,
              title: that.original_object.title,
            }),
            is_verification_needed: true,
            object_approval: true,
            notify_on_change: true,
            notify_custom_message: notifyTemplate({
              name: user.name,
              email: user.email,
              type: that.original_object.constructor.model_singular,
              title: that.original_object.title,
              before: moment(that.end_date).format('MM/DD/YYYY'),
              href: window.location.href.replace(/#.*$/, ''),
            }),
            context: that.original_object.context,
          }).save(createDefaultTaskGroup)
        ).then(function (wf) {
          return $.when(
            wf,
            new CMS.Models.TaskGroup({
              workflow: wf,
              title: reviewTemplate({
                type: that.original_object.constructor.title_singular,
                title: that.original_object.title,
              }),
              contact: that.contact,
              context: wf.context,
            }).save()
          );
        }).then(function (wf, tg) {
          return $.when(
            wf,
            new CMS.Models.TaskGroupTask({
              task_group: tg,
              start_date: moment().format('MM/DD/YYYY'),
              end_date: that.end_date,
              object_approval: true,
              access_control_list: [{
                ac_role_id: assigneeRole.id,
                person: {
                  id: that.contact.id,
                  type: 'Person',
                },
              }],
              context: wf.context,
              task_type: 'text',
              title: reviewTemplate({
                type: that.original_object.constructor.title_singular,
                title: that.original_object.title,
              }),
            }).save(),
            new CMS.Models.TaskGroupObject({
              task_group: tg,
              object: that.original_object,
              context: wf.context,
            }).save()
          );
        });
      } else {
        ret = $.when(
          aws[0].instance.refresh(),
          $.when(...can.map(aws[0].instance.task_groups.reify(),
            function (tg) {
              return tg.refresh();
            })
          ).then(function () {
            return $.when(...can.map(can.makeArray(arguments), function (tg) {
              return tg.attr('contact', that.contact).save().then(function (tg) {
                return $.when(...can.map(tg.task_group_tasks.reify(), function (tgt) {
                  return tgt.refresh().then(function (tgt) {

                    return tgt.attr({
                      'access_control_list': [{
                        ac_role_id: assigneeRole.id,
                        person: {
                          id: that.contact.id,
                          type: 'Person',
                        },
                      }],
                      'end_date': that.end_date,
                      'start_date': moment().format('MM/DD/YYYY'),
                      'task_type': tgt.task_type || 'text',
                    }).save();
                  });
                }));
              });
            }));
          })
        );
      }

      return ret.then(function (wf) {
        let cycleDfd = new CMS.Models.Cycle({
          workflow: wf,
          autogenerate: true,
          context: wf.context,
        }).save();
        cycleDfd.then(function () {
          that.original_object.dispatch(REFRESH_APPROVAL);
        });
        return cycleDfd;
      });
    });
  },
  computed_errors: ApprovalWorkflowErrors,
  computed_unsuppressed_errors: ApprovalWorkflowErrors,
});

export default ModalsController({
  pluginName: 'ggrc_controllers_approval_workflow',
  defaults: {
    original_object: null,
    new_object_form: true,
    model: ApprovalWorkflow,
    modal_title: 'Submit for review',
    custom_save_button_text: 'Submit',
    content_view: GGRC.mustache_path + '/wf_objects/approval_modal_content.mustache',
    button_view: BUTTON_VIEW_SAVE_CANCEL,
    afterFetch: function () {
      this.attr('instance', new ApprovalWorkflow({
        original_object: this.attr('instance'),
      }));
    },
  },
}, {
  init: function () {
    this.options.button_view = BUTTON_VIEW_SAVE_CANCEL;
    this._super(...arguments);
  },
  'input[null-if-empty] change': function (el, ev) {
    if(el.val() === '') {
      this.options.instance.attr(el.attr('name').split('.').slice(0, -1).join('.'), null);
    }
  },
});

export {
  ApprovalWorkflow,
};
