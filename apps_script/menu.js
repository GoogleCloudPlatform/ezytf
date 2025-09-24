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

function invokeEzyTf() {
  const scriptProperties = PropertiesService.getScriptProperties();

  // [SA_NAME]@$[PROJECT].iam.gserviceaccount.com`;
  const invokeServiceAccount = scriptProperties.getProperty("EZTF_INVOKE_SA");
  const ezytfServiceAccount = scriptProperties.getProperty("EZTF_SA");
  // https://[LOCATION]-[PROJECT].cloudfunctions.net/[FUNCTION_NAME]`;
  // https://[CLOUDRUN_NAME]-[PROJECT_NUMBER].[LOCATION].run.app
  const cloudRunUrl = scriptProperties.getProperty("EZTF_CLOUDRUN_URL");

  SpreadsheetApp.getActiveSpreadsheet().addEditor(ezytfServiceAccount);
  let ezytfResponse = invokeTfGeneration(invokeServiceAccount, cloudRunUrl, true);
  EzytfSheet.writeRange(Object.entries(ezytfResponse), "_EzytfResponse");
}

function listFoldersProjects() {
  populateFoldersProjects("folders", "_FoldersProjectPath");
}

function listRolesToSheet() {
  fetchRolesToSheet("_RolesList");
}

function onOpen(e) {
  //custom menu
  SpreadsheetApp.getUi()
    .createMenu("Generate Terraform")
    .addItem("Invoke TF Generate", "invokeEzyTf")
    .addToUi();
  SpreadsheetApp.getUi()
    .createMenu("Custom Load")
    .addItem("Folders & Project Path", "listFoldersProjects")
    .addToUi();
}
