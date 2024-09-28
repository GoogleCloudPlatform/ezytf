function fetchRolesToSheet(writeRangeTitle) {
  const baseUrl = `https://iam.googleapis.com/v1/roles`;
  const headers = {
    Authorization: `Bearer ${ScriptApp.getOAuthToken()}`, // Use OAuth for authentication
  };
  let nextPageToken = null;
  roleData = [];
  do {
    // Construct URL with optional pageToken for pagination
    const url = nextPageToken
      ? `${baseUrl}?pageToken=${nextPageToken}`
      : baseUrl;
    const response = UrlFetchApp.fetch(url, {
      headers: headers,
    });
    const data = JSON.parse(response.getContentText());

    const roles = data.roles || [];
    pageData = roles.map((role) => {
      return [role.name, role.title || ""];
    });

    nextPageToken = data.nextPageToken; // Update for next page if available
    roleData.push(...pageData);
  } while (nextPageToken);
  writeRange(roleData, writeRangeTitle);
}
