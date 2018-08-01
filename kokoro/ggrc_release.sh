#!/bin/bash

# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

set -o nounset
set -o errexit

. /tmpfs/src/gfile/settings

cd "${CURRENT_SCRIPTPATH}/../"
./git_hooks/post-checkout

CONFIG_PREFIX="./extras/deploy/"
PROJECT_NAME="$APPENGINE_INSTANCE"
CONFIG_DIR="$CONFIG_PREFIX/$PROJECT_NAME/"

mkdir -p "$CONFIG_DIR"

SERVICE_ACCOUNT="$SERVICE_ACCOUNT"
SERVICE_ACCOUNT_FILE="$CONFIG_DIR/service-account"
KEY_FILE="$CONFIG_DIR/$SERVICE_ACCOUNT.key"
SETTINGS_FILE="$CONFIG_DIR/settings.sh"

echo $SERVICE_ACCOUNT > "$SERVICE_ACCOUNT_FILE"

# Fill in private.key with the user's private key
cat >"$KEY_FILE" <<EOL
{
  "type": "$ACCOUNT_TYPE",
  "project_id": "$PROJECT_ID",
  "private_key_id": "$PRIVATE_KEY_ID",
  "private_key": "$PRIVATE_KEY",
  "client_email": "$CLIENT_EMAIL",
  "client_id": "$CLIENT_ID",
  "auth_uri": "$AUTH_URI",
  "token_uri": "$TOKEN_URI",
  "auth_provider_x509_cert_url": "$AUTH_PROVIDER_X509_CERT_URL",
  "client_x509_cert_url": "$CLIENT_X509_CERT_URL"
}
EOL


cat >"$SETTINGS_FILE" <<EOL
#!/usr/bin/env bash
APPENGINE_INSTANCE="$APPENGINE_INSTANCE"
SETTINGS_MODULE="$SETTINGS_MODULE"
DATABASE_URI="$DATABASE_URI"
SECRET_KEY="$SECRET_KEY"
GOOGLE_ANALYTICS_ID="$GOOGLE_ANALYTICS_ID"
GOOGLE_ANALYTICS_DOMAIN="$GOOGLE_ANALYTICS_DOMAIN"
GAPI_KEY="$GAPI_KEY"
GAPI_CLIENT_ID="$GAPI_CLIENT_ID"
GAPI_CLIENT_SECRET="$GAPI_CLIENT_SECRET"
GAPI_ADMIN_GROUP="$GAPI_ADMIN_GROUP"
BOOTSTRAP_ADMIN_USERS="$BOOTSTRAP_ADMIN_USERS"
MIGRATOR="$MIGRATOR"
RISK_ASSESSMENT_URL="$RISK_ASSESSMENT_URL"
ABOUT_URL="$ABOUT_URL"
ABOUT_TEXT="$ABOUT_TEXT"
EXTERNAL_HELP_URL="$EXTERNAL_HELP_URL"
EXTERNAL_IMPORT_HELP_URL="$EXTERNAL_IMPORT_HELP_URL"
INSTANCE_CLASS="$INSTANCE_CLASS"
MAX_INSTANCES="$MAX_INSTANCES"
CUSTOM_URL_ROOT="$CUSTOM_URL_ROOT"
SCALING="$SCALING"
GGRC_Q_INTEGRATION_URL="$GGRC_Q_INTEGRATION_URL"
INTEGRATION_SERVICE_URL="$INTEGRATION_SERVICE_URL"
EXTERNAL_APP_USER="$EXTERNAL_APP_USER"
URLFETCH_SERVICE_ID="$URLFETCH_SERVICE_ID"
DASHBOARD_INTEGRATION="$DASHBOARD_INTEGRATION"
ALLOWED_QUERYAPI_APP_IDS="$ALLOWED_QUERYAPI_APP_IDS"
APPENGINE_EMAIL="$APPENGINE_EMAIL"
AUTHORIZED_DOMAIN="$AUTHORIZED_DOMAIN"
ACCESS_TOKEN="$ACCESS_TOKEN"
ISSUE_TRACKER_ENABLED="$ISSUE_TRACKER_ENABLED"
ISSUE_TRACKER_BUG_URL_TMPL="$ISSUE_TRACKER_BUG_URL_TMPL"
VERSION="$VERSION"
KOKORO=true
COMPANY="$COMPANY"
COMPANY_LOGO_TEXT="$COMPANY_LOGO_TEXT"
CREATE_ISSUE_URL="$CREATE_ISSUE_URL"
CREATE_ISSUE_BUTTON_NAME="$CREATE_ISSUE_BUTTON_NAME"
EOL

./bin/deploy $APPENGINE_INSTANCE
