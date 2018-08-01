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
    describe('mapDocuments() method', () => {
      let checkDocumentsExistDfd;

      beforeEach(() => {
        checkDocumentsExistDfd = can.Deferred();
        spyOn(viewModel, 'checkDocumentsExist').and
          .returnValue(checkDocumentsExistDfd);
      });

      it('should check wheteher documents already exist', () => {
        let file = {};
        spyOn(viewModel, 'createDocuments')
          .and.returnValue(can.Deferred().resolve([]));
        spyOn(viewModel, 'useExistingDocuments')
          .and.returnValue(can.Deferred().resolve([]));

        viewModel.mapDocuments(file);

        expect(viewModel.checkDocumentsExist).toHaveBeenCalledWith(file);
      });

      it('should create a new documents if they are not exist', (done) => {
        let file = {id: 1};
        spyOn(viewModel, 'createDocuments')
          .and.returnValue(can.Deferred().resolve([]));
        spyOn(viewModel, 'useExistingDocuments')
          .and.returnValue(can.Deferred().resolve([]));

        viewModel.mapDocuments([file]);

        checkDocumentsExistDfd.resolve([{
          exists: false,
          gdrive_id: 1,
        }]).then(() => {
          expect(viewModel.createDocuments).toHaveBeenCalledWith([file]);
          done();
        });
      });

      it('should attach existing documents if they are already exists',
        (done) => {
          let file = {};
          let response = [{
            exists: true,
            object: {},
          }];
          spyOn(viewModel, 'createDocuments')
            .and.returnValue(can.Deferred().resolve([]));
          spyOn(viewModel, 'useExistingDocuments')
            .and.returnValue(can.Deferred().resolve([]));

          viewModel.mapDocuments([file]);

          checkDocumentsExistDfd.resolve(response).then(() => {
            expect(viewModel.useExistingDocuments)
              .toHaveBeenCalledWith(response);
            done();
          });
        });

      it('should create new and attach existing documents', (done) => {
        let file1 = {id: 1};
        let file2 = {id: 2};
        let files = [file1, file2];

        let existingDocument = {
          gdrive_id: 1,
          exists: true,
          object: existingDocument,
        };
        let notExistingDocument = {
          gdrive_id: 2,
          exists: false,
        };

        spyOn(viewModel, 'createDocuments')
          .and.returnValue(can.Deferred().resolve([]));
        spyOn(viewModel, 'useExistingDocuments')
          .and.returnValue(can.Deferred().resolve([]));

        viewModel.mapDocuments(files);

        checkDocumentsExistDfd.resolve([
          existingDocument,
          notExistingDocument,
        ]).then(() => {
          expect(viewModel.useExistingDocuments)
            .toHaveBeenCalledWith([existingDocument]);
          expect(viewModel.createDocuments)
            .toHaveBeenCalledWith([file2]);
          done();
        });
      });

      it('should refresh permissions and map documents', (done) => {
        let document1 = {};
        let document2 = {};
        spyOn(viewModel, 'refreshPermissionsAndMap');
        spyOn(viewModel, 'createDocuments')
          .and.returnValue(can.Deferred().resolve([document1]));
        spyOn(viewModel, 'useExistingDocuments')
          .and.returnValue(can.Deferred().resolve([document2]));

        viewModel.mapDocuments([]);

        checkDocumentsExistDfd.resolve([]).then(() => {
          expect(viewModel.refreshPermissionsAndMap)
            .toHaveBeenCalledWith([document1, document2]);
          done();
        });
      });
    });

    describe('createDocuments() method', () => {
      it('should dispatch beforeDocumentCreate event before saving document',
        () => {
          let parentInstance = viewModel.attr('parentInstance');
          spyOn(parentInstance, 'dispatch');
          spyOn(CMS.Models.Document.prototype, 'save').and.returnValue({});

          viewModel.createDocuments([{}]);

          expect(parentInstance.dispatch)
            .toHaveBeenCalledWith(BEFORE_DOCUMENT_CREATE);
        });

      it('should return new document after saving', (done) => {
        let saveDfd = can.Deferred();
        let newDocument = {};
        spyOn(CMS.Models.Document.prototype, 'save').and.returnValue(saveDfd);

        viewModel.createDocuments([{}]);

        saveDfd.resolve(newDocument)
          .then((document) => {
            expect(document).toBe(newDocument);
            done();
          });
      });

      it('should dispatch documentCreateFailed event if document is not saved',
        (done) => {
          let parentInstance = viewModel.attr('parentInstance');
          spyOn(parentInstance, 'dispatch');

          spyOn(CMS.Models.Document.prototype, 'save')
            .and.returnValue(can.Deferred().reject());

          let result = viewModel.createDocuments([{}]);

          result.fail(() => {
            expect(parentInstance.dispatch.calls.mostRecent().args)
              .toEqual([DOCUMENT_CREATE_FAILED]);
            done();
          });
        });
    });

    describe('useExistingDocuments() method', () => {
      let showConfirmDfd;

      beforeEach(() => {
        showConfirmDfd = can.Deferred();
        spyOn(viewModel, 'showConfirm').and.returnValue(showConfirmDfd);
      });

      it('should show confirm modal', () => {
        viewModel.useExistingDocuments([{}]);

        expect(viewModel.showConfirm).toHaveBeenCalled();
      });

      it('should add current user to document admins', (done) => {
        let document = {};
        spyOn(viewModel, 'makeAdmin');

        viewModel.useExistingDocuments([document]);

        showConfirmDfd.resolve()
          .then(() => {
            expect(viewModel.makeAdmin).toHaveBeenCalledWith([document]);
            done();
          });
      });
    });

    describe('refreshPermissionsAndMap() method', () => {
      it('should close object-mapper if there are nothing to map', () => {
        let element = {
          trigger: jasmine.createSpy(),
        };
        viewModel.attr('element', element);

        viewModel.refreshPermissionsAndMap([]);

        expect(element.trigger).toHaveBeenCalledWith('modal:dismiss');
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

      beforeEach(() => {
        let context = {
          viewModel,
          attach: jasmine.createSpy(),
        };
        handler = events['.pick-file click'].bind(context);

        uploadFilesDfd = can.Deferred();
        spyOn(pickerUtils, 'uploadFiles').and.returnValue(uploadFilesDfd);
        spyOn(viewModel, 'mapDocuments');
      });

      it('should call uploadFiles method', () => {
        handler();

        expect(pickerUtils.uploadFiles).toHaveBeenCalled();
      });

      it('should call mapDocuments method if file is picked', (done) => {
        let file = {};
        let files = [file];

        handler();

        uploadFilesDfd.resolve(files)
          .then(() => {
            expect(viewModel.mapDocuments).toHaveBeenCalledWith([file]);
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
  });
});
