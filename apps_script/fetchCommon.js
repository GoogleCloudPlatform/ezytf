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
