/*
  Copyright (C) 2018 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import Pagination from '../../base-objects/pagination';
import {getComponentVM} from '../../../../js_specs/spec_helpers';
import Component from '../tree_pagination';

describe('tree-pagination component', function () {
  let viewModel;

  beforeAll(function () {
    viewModel = getComponentVM(Component);
  });

  beforeEach(function () {
    viewModel.attr('paging', new Pagination({
      pageSize: 10,
      disabled: false,
    }));
    viewModel.paging.attr('count', 3);
    viewModel.paging.attr('current', 1);
  });

  describe('paginationInfo() method in helpers', function () {
    it('returns info about visible items on page', function () {
      let result;
      viewModel.attr('paging.pageSize', 10);
      viewModel.attr('paging.total', 3000);
      viewModel.attr('paging.current', 15);
      result = viewModel.getPaginationInfo();
      expect(result).toEqual('141-150 of 3000');
    });

    it('returns "No records" if we don\'t have elements', function () {
      let result;
      viewModel.paging.attr('current', 0);
      viewModel.paging.attr('total', 0);
      result = viewModel.getPaginationInfo();
      expect(result).toEqual('No records');
    });
  });
  describe('setNextPage() method ', function () {
    it('changes current and increase it by 1', function () {
      viewModel.paging.attr('current', 1);
      viewModel.paging.attr('count', 3);
      viewModel.setNextPage();
      expect(viewModel.paging.current).toEqual(2);
    });
    it('doesn\'t change current value if current equal amount of pages',
      function () {
        viewModel.paging.attr('current', 3);
        viewModel.setNextPage();
        expect(viewModel.paging.current).toEqual(3);
      });
  });
  describe('setPrevPage() method ', function () {
    it('changes current and decrease it by 1', function () {
      viewModel.paging.attr('current', 2);
      viewModel.setPrevPage();
      expect(viewModel.paging.current).toEqual(1);
    });
    it('doesn\'t change current value if current equal 1',
      function () {
        viewModel.paging.attr('current', 1);
        viewModel.setPrevPage();
        expect(viewModel.paging.current).toEqual(1);
      });
  });
  describe('setFirstPage() method ', function () {
    it('changes current if current more than 1', function () {
      viewModel.paging.attr('current', 3);
      viewModel.setFirstPage();
      expect(viewModel.paging.current).toEqual(1);
    });
  });
  describe('setLastPage() method ', function () {
    it('changes current if current less than amount of pages', function () {
      viewModel.paging.attr('count', 3);
      viewModel.paging.attr('current', 2);
      viewModel.setLastPage();
      expect(viewModel.paging.current).toEqual(3);
    });
  });
  describe('setCurrentPage() method ', function () {
    it('changes current page',
      function () {
        viewModel.setCurrentPage(2);
        expect(viewModel.paging.current).toEqual(2);
      });
  });
  describe('setPageSize() method ', function () {
    it('sets page size',
      function () {
        viewModel.setPageSize(50);
        expect(viewModel.paging.pageSize).toEqual(50);
      });
  });
  describe('pagesList() method ', function () {
    it('returns array of pages',
      function () {
        viewModel.paging.attr('count', 11);
        let result = viewModel.pagesList();
        expect(result.length).toEqual(11);
      });
    it('returns current indexes',
      function () {
        viewModel.paging.attr('count', 12);
        let result = viewModel.pagesList();
        expect(result[0]).toEqual(1);
        expect(result[11]).toEqual(12);
      });
  });
  describe('getPageTitle() method ', function () {
    it('returns correct title',
      function () {
        viewModel.paging.attr('pageSize', 15);
        viewModel.paging.attr('total', 56);

        let result = viewModel.getPageTitle(1);
        expect(result).toEqual('Page 1: 1-15');

        result = viewModel.getPageTitle(4);
        expect(result).toEqual('Page 4: 46-56');
      });
  });
});
