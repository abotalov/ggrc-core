/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

import {initWidgets} from '../../plugins/utils/current-page-utils';
import {gapiClient} from '../../plugins/ggrc-gapi-client';

gapiClient.loadGapiClient();

$('#csv_export')
  .html(can.view.mustache('<csv-export filename="Export Objects"/>'));
$('#page-header').html(can.view.mustache('<page-header/>'));
initWidgets();
