/*
 Copyright (C) 2018 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

/**
 @description
 Date formats for the actual selected value, and for the date as
 displayed to the user. The Moment.js library and the jQuery datepicker
 use different format notation, thus separate settings for each.
 IMPORTANT: The pair of settings for each "type" of value (i.e. actual
 value / display value) must be consistent across both libraries!
*/
const DATE_FORMAT = {
  MOMENT_ISO_DATE: 'YYYY-MM-DD',
  MOMENT_DISPLAY_FMT: 'MM/DD/YYYY',
  PICKER_ISO_DATE: 'yy-mm-dd',
  PICKER_DISPLAY_FMT: 'mm/dd/yy',
  ISO_SHORT: 'YYYY-MM-DDTHH:mm:ss',
};

/**
 * Adjust date to the closest week day that is less than current.
 *
 * @param {Date} date - date value
 *
 * @return {Date} closest week date to provided
 */
function getClosestWeekday(date) {
  let momDate = moment(date);

  if (momDate.isoWeekday() > 5) {
    return momDate.isoWeekday(5).toDate();
  }

  return date;
}

/**
 * Convert given Date, string or null to an Date object.
 *
 * @param {Date|string|null} date - Date, string in ISO date format or null
 * @param {string} format - date format string ('YYYY-MM-DD' default value)
 * @return {string|null} - Date object or null if string is not in ISO format or null
 */
function getDate(date, format = DATE_FORMAT.MOMENT_ISO_DATE) {
  let momDate;

  if (date instanceof Date) {
    return date;
  }

  momDate = moment(date, format, true);
  if (momDate.isValid()) {
    return momDate.toDate();
  }

  return null;
}

/**
 * Convert given Date to UTC string.
 *
 * @param {Date|string} date - Date or string in ISO date format
 * @param {string} format - date format string ('YYYY-MM-DDTHH:mm:ss' default value)
 * @return {string} - formatted date string in UTC
 */
function getUtcDate(date, format = DATE_FORMAT.ISO_SHORT) {
  return moment.utc(date).format(format);
}

export {
  DATE_FORMAT,
  getClosestWeekday,
  getDate,
  getUtcDate,
};
