function invokeEzyTf() {
  const scriptProperties = PropertiesService.getScriptProperties();

  // [SA_NAME]@$[PROJECT].iam.gserviceaccount.com`;
  const invokeServiceAccount = scriptProperties.getProperty("EZTF_INVOKE_SA");
  const ezytfServiceAccount = scriptProperties.getProperty("EZTF_SA");
  // https://[LOCATION]-[PROJECT].cloudfunctions.net/[FUNCTION_NAME]`;
  // https://[CLOUDRUN_NAME]-[PROJECT_NUMBER].[LOCATION].run.app
  const cloudRunUrl = scriptProperties.getProperty("EZTF_CLOUDRUN_URL");

  SpreadsheetApp.getActiveSpreadsheet().addEditor(ezytfServiceAccount);
  invokeTfGeneration(invokeServiceAccount, cloudRunUrl, true);
}

function populateFoldersProjects() {
  populateFoldersProjects("folders", "_FoldersProjectPath");
}

function fetchRolesToSheet() {
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
    .addItem("Folders & Project Path", "populateFoldersProjects")
    .addToUi();
}
