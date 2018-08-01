/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Component from './release-notes-menu-item';
import {getComponentVM} from '../../../js_specs/spec_helpers';
import * as UserUtils from '../../plugins/utils/user-utils';
import {getUtcDate} from '../../plugins/utils/date-util';

describe('"release-notes-menu-item" component', () => {
  let vm;

  beforeEach(() => {
    vm = getComponentVM(Component);
  });

  describe('open() method', () => {
    it('sets true to "state.open" flag', () => {
      vm.attr('state.open', false);

      vm.open();

      expect(vm.attr('state.open')).toBe(true);
    });
  });

  describe('events', () => {
    let events;
    let handler;

    beforeEach(() => {
      events = Component.prototype.events;
    });

    describe('"inserted" handler', () => {
      const releaseDateObj = new Date(RELEASE_NOTES_DATE);
      let profileDfd;

      beforeEach(() => {
        handler = events.inserted.bind({viewModel: vm});
        spyOn(vm, 'open');

        profileDfd = can.Deferred();
        spyOn(UserUtils, 'loadUserProfile')
          .and.returnValue(profileDfd);
        spyOn(UserUtils, 'updateUserProfile')
          .and.returnValue(profileDfd);
      });

      describe('if RELEASE_NOTES_DATE not equal to saved date', () => {
        let dayBefore;
        let profile;

        beforeEach(() => {
          dayBefore = new Date(releaseDateObj)
            .setDate(releaseDateObj.getDate() - 1);
          profile = {
            last_seen_whats_new: new Date(dayBefore).toISOString(),
          };
          profileDfd.resolve(profile);
        });

        it('calls updateUserProfile with RELEASE_NOTES_DATE', async (done) => {
          let updatedProfile = {
            last_seen_whats_new: getUtcDate(releaseDateObj),
          };
          await handler();

          expect(UserUtils.updateUserProfile)
            .toHaveBeenCalledWith(updatedProfile);
          done();
        });

        it('calls open() method', async (done) => {
          await handler();
          expect(vm.open).toHaveBeenCalled();
          done();
        });
      });

      describe('if RELEASE_NOTES_DATE equal to saved date', () => {
        let profile;

        beforeEach(() => {
          profile = {
            last_seen_whats_new: new Date(releaseDateObj).toISOString(),
          };
          profileDfd.resolve(profile);
        });

        it('updateUserProfile() should not been called', async (done) => {
          await handler();

          expect(UserUtils.updateUserProfile)
            .not.toHaveBeenCalled();
          done();
        });

        it('open() should not been called', async (done) => {
          await handler();
          expect(vm.open).not.toHaveBeenCalled();
          done();
        });
      });
    });
  });
});
