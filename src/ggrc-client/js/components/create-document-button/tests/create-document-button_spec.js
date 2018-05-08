/*
  Copyright (C) 2018 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Component from '../create-document-button';
import {getComponentVM} from '../../../../js_specs/spec_helpers';
import * as pickerUtils from '../../../plugins/utils/gdrive-picker-utils';
import {
  BEFORE_DOCUMENT_CREATE,
  DOCUMENT_CREATE_FAILED,
} from '../../../events/eventTypes';

describe('CreateDocumentButton component', () => {
  let viewModel;
  beforeEach(() => {
    viewModel = getComponentVM(Component);
    viewModel.attr('parentInstance', {});
  });

  describe('viewModel', () => {
    describe('mapDocument() method', () => {
      let checkDocumentExistsDfd;

      beforeEach(() => {
        checkDocumentExistsDfd = can.Deferred();
        spyOn(viewModel, 'checkDocumentExists').and
          .returnValue(checkDocumentExistsDfd);
      });

      it('should check wheteher document already exists', () => {
        let file = {};
        viewModel.mapDocument(file);

        expect(viewModel.checkDocumentExists).toHaveBeenCalledWith(file);
      });

      it('should create a new document if it is not exist', (done) => {
        let file = {};
        spyOn(viewModel, 'createDocument');

        viewModel.mapDocument(file);

        checkDocumentExistsDfd.resolve({
          status: 'not exists',
        }).then(() => {
          expect(viewModel.createDocument).toHaveBeenCalledWith(file);
          done();
        });
      });

      it('should attach existing document if it already exists', (done) => {
        let file = {};
        let existingDocument = {};
        spyOn(viewModel, 'useExistingDocument');

        viewModel.mapDocument(file);

        checkDocumentExistsDfd.resolve({
          status: 'exists',
          object: existingDocument,
        }).then(() => {
          expect(viewModel.useExistingDocument)
            .toHaveBeenCalledWith(existingDocument);
          done();
        });
      });

      it('should refresh permissions and map document', (done) => {
        let document = {};
        spyOn(viewModel, 'refreshPermissionsAndMap');
        spyOn(viewModel, 'createDocument').and.returnValue(document);

        viewModel.mapDocument({});

        checkDocumentExistsDfd.resolve({
          status: 'not exists',
        }).then(() => {
          expect(viewModel.refreshPermissionsAndMap)
            .toHaveBeenCalledWith(document);
          done();
        });
      });
    });

    describe('createDocument() method', () => {
      it('should dispatch beforeDocumentCreate event before saving document',
        () => {
          let parentInstance = viewModel.attr('parentInstance');
          spyOn(parentInstance, 'dispatch');

          viewModel.createDocument({});

          expect(parentInstance.dispatch)
            .toHaveBeenCalledWith(BEFORE_DOCUMENT_CREATE);
        });

      it('should return new document after saving', (done) => {
        let saveDfd = can.Deferred();
        let newDocument = {};
        spyOn(CMS.Models.Document.prototype, 'save').and.returnValue(saveDfd);

        viewModel.createDocument({});

        saveDfd.resolve(newDocument)
          .then((document) => {
            expect(document).toBe(newDocument);
            done();
          });
      });

      it('should dispatch documentCreateFailed event if document is not saved',
        (done) => {
          let saveDfd = can.Deferred();
          let parentInstance = viewModel.attr('parentInstance');
          spyOn(parentInstance, 'dispatch');

          spyOn(CMS.Models.Document.prototype, 'save').and.returnValue(saveDfd);

          viewModel.createDocument({});

          saveDfd.reject()
            .fail(() => {
              expect(parentInstance.dispatch.calls.mostRecent().args)
                .toEqual([DOCUMENT_CREATE_FAILED]);
              done();
            });
        });
    });

    describe('useExistingDocument() method', () => {
      let showConfirmDfd;

      beforeEach(() => {
        showConfirmDfd = can.Deferred();
        spyOn(viewModel, 'showConfirm').and.returnValue(showConfirmDfd);
      });

      it('should show confirm modal', () => {
        viewModel.useExistingDocument();

        expect(viewModel.showConfirm).toHaveBeenCalled();
      });

      it('should add current user to document admins', (done) => {
        let document = {};
        spyOn(viewModel, 'makeAdmin');

        viewModel.useExistingDocument(document);

        showConfirmDfd.resolve()
          .then(() => {
            expect(viewModel.makeAdmin).toHaveBeenCalledWith(document);
            done();
          });
      });
    });
  });

  describe('events', () => {
    let events;

    beforeAll(() => {
      events = Component.prototype.events;
    });

    describe('.pick-file click handler', () => {
      let handler;
      let uploadFilesDfd;
      let context;

      beforeEach(() => {
        context = {
          viewModel,
          attach: jasmine.createSpy(),
        };
        handler = events['.pick-file click'].bind(context);

        uploadFilesDfd = can.Deferred();
        spyOn(pickerUtils, 'uploadFiles').and.returnValue(uploadFilesDfd);
      });

      it('should call uploadFiles method', () => {
        handler();

        expect(pickerUtils.uploadFiles).toHaveBeenCalled();
      });

      it('should call attach method if file is picked', (done) => {
        let file = {};
        let files = [file];

        handler();

        uploadFilesDfd.resolve(files)
          .then(() => {
            expect(context.attach).toHaveBeenCalledWith(file);
            done();
          });
      });

      it('should trigger modal:dismiss event if file is not picked', (done) => {
        spyOn($.prototype, 'trigger');
        handler();

        uploadFilesDfd.reject()
          .fail(() => {
            expect($.prototype.trigger).toHaveBeenCalledWith('modal:dismiss');
            expect($.prototype.trigger.calls.mostRecent().object[0])
              .toEqual(window);
            done();
          });
      });
    });

    describe('attach() method', () => {
      let handler;
      let mapDocumentDfd;
      let element;

      beforeEach(() => {
        element = {
          trigger: jasmine.createSpy(),
        };

        handler = events.attach.bind({
          viewModel,
          element,
        });

        mapDocumentDfd = can.Deferred();
        spyOn(viewModel, 'mapDocument').and
          .returnValue(mapDocumentDfd);
      });

      it('should call mapDocument', () => {
        let file = {};
        handler(file);
        expect(viewModel.mapDocument).toHaveBeenCalledWith(file);
      });

      it(`should trigger modal:dismiss event
        when document mapping is failed`,
        (done) => {
          handler({});

          mapDocumentDfd.reject()
            .fail(() => {
              expect(element.trigger)
                .toHaveBeenCalledWith('modal:dismiss');
              done();
            });
        });
    });
  });
});
