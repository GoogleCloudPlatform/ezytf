/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

function invokeTfGeneration(serviceAccount, cloudRunUrl, generateCode = false) {
  try {
    const spreadsheetId = SpreadsheetApp.getActiveSpreadsheet().getId();
    const saTokenUrl = `https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${serviceAccount}:generateIdToken`;

    console.log(spreadsheetId);
    var options = {
      method: "post",
      headers: { Authorization: "Bearer " + ScriptApp.getOAuthToken() },
      contentType: "application/json",
      payload: JSON.stringify({
        includeEmail: true,
        audience: cloudRunUrl,
      }),
    };
    var tokenResponse = UrlFetchApp.fetch(saTokenUrl, options);
    var runOptions = {
      method: "POST",
      contentType: "application/json",
      payload: JSON.stringify({
        spreadsheetId: spreadsheetId,
        generateCode: generateCode,
      }),
      headers: {
        Authorization:
          "Bearer " + JSON.parse(tokenResponse.getContentText()).token,
      },
    };
    var response = UrlFetchApp.fetch(cloudRunUrl, runOptions);
    Logger.log(response.getContentText());
    return JSON.parse(response.getContentText())
  } catch (error) {
    console.error("Error invoking Cloud Function:", error);
    SpreadsheetApp.getUi().alert("An error occurred.");
    return {}
  }
}
