/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import {
  getClosestWeekday,
  getDate,
  getUtcDate,
} from '../utils/date-util';

describe('GGRC DateUtil', ()=> {
  describe('getClosestWeekday() method', ()=> {
    it('adjusts to Friday when weekend provided', ()=> {
      let date = new Date(2017, 11, 24);
      let actual;

      actual = getClosestWeekday(date);

      expect(actual.getDate()).toEqual(22);
    });

    it('leaves date as is when week day provided', ()=> {
      let date = new Date(2017, 11, 20);
      let actual;

      actual = getClosestWeekday(date);

      expect(actual.getDate()).toEqual(20);
    });
  });

  describe('getDate() method', function () {
    it('returns date for Date object parameter', function () {
      let expected = new Date();
      let actual = getDate(expected);

      expect(actual).toEqual(expected);
    });

    it('returns null for null parameter', function () {
      let actual = getDate(null);

      expect(actual).toBeNull();
    });

    describe('when date format is not specified', function () {
      it('returns null for Date in moment display format', function () {
        let param = '04/30/2017';
        let actual = getDate(param);

        expect(actual).toBeNull();
      });

      it('returns null for Date in picker ISO format', function () {
        let param = '17-04-30';
        let actual = getDate(param);

        expect(actual).toBeNull();
      });

      it('returns null for Date in picker display format', function () {
        let param = '04/30/17';
        let actual = getDate(param);

        expect(actual).toBeNull();
      });

      it('returns correct Date for Date in moment ISO format', function () {
        let dateString = '2017-04-30';
        let expected = new Date(2017, 3, 30);
        let actual = getDate(dateString);

        expect(actual).toEqual(expected);
      });
    });

    it('returns null when date string is not in correct date format',
      function () {
        let dateString = '2017/04/30';
        let dateFormat = 'YYYY/DD/MM';
        let actual = getDate(dateString, dateFormat);

        expect(actual).toBeNull();
      });

    it('returns expected Date when date string is in correct date format',
      function () {
        let dateString = '2017/30/04';
        let dateFormat = 'YYYY/DD/MM';
        let expected = new Date(2017, 3, 30);
        let actual = getDate(dateString, dateFormat);

        expect(actual).toEqual(expected);
      });
  });

  describe('getUtcDate() method', ()=> {
    let date;
    let result;
    let expectedDefaultResult;

    beforeEach(() => {
      date = '2018-07-24';
      expectedDefaultResult = '2018-07-24T00:00:00';
    });

    it('returns ISO_SHORT format when no format provided', () => {
      result = getUtcDate(date);

      expect(result).toEqual(expectedDefaultResult);
    });

    it('returns string when Date object passed', () => {
      let dateObj = new Date(date);
      result = getUtcDate(dateObj);

      expect(result).toEqual(expectedDefaultResult);
    });

    it('returns string of specific format', () => {
      let format = 'MM/DD/YYYY';
      result = getUtcDate(date, format);

      let expectedFormat = '07/24/2018';

      expect(result).toEqual(expectedFormat);
    });
  });
});
