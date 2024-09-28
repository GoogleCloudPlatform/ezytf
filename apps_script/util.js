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

function cleanKey(str) {
  if (!str) str = "";
  return lower(sepArray(str, ":").join("."));
}

function lower(str) {
  if (!str) str = "";
  return rpSpaces(rmBracket(str)).toLowerCase();
}

function rpSpaces(str) {
  if (!str) str = "";
  return str.trim().replace(/\s+/g, "_");
}

function rmBracket(str) {
  if (!str) str = "";
  return str.replace(/\s*\(.*\)/, "").trim();
}

function sepArray(str, sep = ",") {
  if (!str) str = "";
  return str
    .split(sep)
    .map((value) => value.trim())
    .filter((value) => value);
}

function mapData([headers, values], modifyEntry = () => {}) {
  const data = values
    .map((row) => {
      let obj = {};
      if (row.every((str) => !str)) {
        return {};
      }
      headers.forEach((header, index) => {
        obj[header] = row[index];
      });

      if (modifyEntry) {
        obj = modifyEntry(obj);
      }
      return obj;
    })
    .filter((obj) => !!obj && Object.keys(obj).length > 0);
  return data;
}

function readVerticalRange(rangeName, keyMap = {}, skipHeader = true) {
  sheet = SpreadsheetApp.getActiveSpreadsheet();
  range = sheet.getRangeByName(rangeName);
  var values = range.getValues();
  data = {};
  if (skipHeader) values = values.slice(1);
  for (const row of values) {
    key = cleanKey(row[0]);
    key = keyMap[key] || key;
    if (key) {
      data[key] = row.slice(1);
    }
  }
  return data;
}

function readNamedRange(rangeName, keyMap = {}) {
  sheet = SpreadsheetApp.getActiveSpreadsheet();
  range = sheet.getRangeByName(rangeName);
  if (!range) {
    return [[], [], rangeName];
  }
  var values = range.getValues();
  let headers = values[0];
  let rangeValue = values.slice(1);
  const newheaders = headers.map((key) => {
    key = cleanKey(key);
    return keyMap[key] || key;
  });
  return [newheaders, rangeValue];
}

function writeRange(data, tname) {
  sheet = SpreadsheetApp.getActiveSpreadsheet();
  range = sheet.getRangeByName(tname);
  wRow = range.getRow() + 1;
  wCol = range.getColumn();
  writeRange = range
    .getSheet()
    .getRange(wRow, wCol, data.length, data[0].length);
  writeRange.setValues(data);
}

function clearContentColumn(rangeTitle, rowLength) {
  sheet = SpreadsheetApp.getActiveSpreadsheet();
  range = sheet.getRangeByName(rangeTitle);
  wRow = range.getRow() + 1;
  wCol = range.getColumn();
  clearRange = range.getSheet().getRange(wRow, wCol, rowLength, 1);
  clearRange.clearContent();
}
