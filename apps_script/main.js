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
  } catch (error) {
    console.error("Error invoking Cloud Function:", error);
    SpreadsheetApp.getUi().alert("An error occurred.");
  }
}
