import {
  getTfRanges,
  setRangeDataByName,
  formatHeaderData,
} from "../format.js";
import { GoogleAuth } from "google-auth-library";
import { google } from "googleapis";
export { readSheetRanges };

const SCOPES = [
  "https://www.googleapis.com/auth/spreadsheets.readonly",
  "https://www.googleapis.com/auth/drive.file",
];

const selectedRangeName = "tfgenerate";

async function readSheetRanges(eztf, spreadsheetId) {
  const auth = new GoogleAuth({
    scopes: SCOPES,
  });

  const sheets = google.sheets({ version: "v4", auth });

  console.log("Reading Google Sheet: ", spreadsheetId);
  // Get Named Ranges
  const namedRangesResponse = await sheets.spreadsheets.get({
    spreadsheetId,
    fields: "namedRanges(name,range)",
  });

  const namedRanges = namedRangesResponse.data.namedRanges;

  // Read tf Range
  const rangesResponse = await sheets.spreadsheets.values.get({
    spreadsheetId,
    range: selectedRangeName,
    valueRenderOption: "UNFORMATTED_VALUE",
  });

  // Intersect named ranges and selected ranges
  setRangeDataByName(eztf, selectedRangeName, rangesResponse.data.values);

  const [tfRanges, verticalTfRange] = getTfRanges(eztf, selectedRangeName);
  const listTfRanges = Object.values(tfRanges)
    .flat(2)
    .map((val) => Object.keys(val))
    .flat();

  // range list string
  const allTfRanges = [...["variable"], ...listTfRanges];
  const verticalRangesList = [...["variable"], ...verticalTfRange];
  const sheetRanges = namedRanges.map((range) => range.name);
  const validRanges = allTfRanges.filter((value) =>
    sheetRanges.includes(value)
  );
  const validRangesObj = namedRanges.filter((range) =>
    validRanges.includes(range.name)
  );
  const horizontalRanges = validRanges.filter(
    (value) => !verticalRangesList.includes(value)
  );
  const verticalRanges = verticalRangesList.filter((value) =>
    validRanges.includes(value)
  );
  console.log("Horizontal Ranges:", horizontalRanges);
  console.log("Vertical Ranges:", verticalRanges);
  var horizonatalValues = [];
  var verticalValues = [];

  // BatchGet Horizonatal Range Values
  if (horizontalRanges.length > 0) {
    const hzValuesResponse = await sheets.spreadsheets.values.batchGet({
      spreadsheetId,
      ranges: horizontalRanges,
      valueRenderOption: "UNFORMATTED_VALUE",
    });
    if (hzValuesResponse.data) {
      horizonatalValues = hzValuesResponse.data.valueRanges || [];
    }
  }

  // BatchGet Vertical Range Values
  if (verticalRanges.length > 0) {
    const vrValuesResponse = await sheets.spreadsheets.values.batchGet({
      spreadsheetId,
      ranges: verticalRanges,
      majorDimension: "COLUMNS",
      valueRenderOption: "UNFORMATTED_VALUE",
    });
    if (vrValuesResponse.data) {
      verticalValues = vrValuesResponse.data.valueRanges || [];
    }
  }

  // Horizonatal Range values
  horizonatalValues.forEach((rangeData, index) => {
    setRangeDataByName(eztf, horizontalRanges[index], rangeData.values);
  });
  // Vertical Range values
  verticalValues.forEach((rangeData, index) => {
    setRangeDataByName(eztf, verticalRanges[index], rangeData.values);
  });

  // Range Filter Header Request for notes
  let [dataFilters, rangeRowNameMap] = rangeFilterHeader(
    validRangesObj,
    verticalRanges
  );

  // Get Range Header Notes
  const notesResponse = await sheets.spreadsheets.getByDataFilter({
    spreadsheetId,
    fields:
      "sheets(properties(sheetId),data(startRow,startColumn,rowData(values(formattedValue,note))))",
    requestBody: {
      dataFilters: dataFilters,
      includeGridData: true,
    },
  });

  eztf.rangeNoteKey = noteFieldMetadata(notesResponse.data, rangeRowNameMap);

  // console.log(JSON.stringify(dataFilters,null,2));
  // console.log(JSON.stringify(rangeRowNameMap, null, 2));
  // console.log(JSON.stringify(notesResponse.data, null, 2));

  return tfRanges;
}

function noteFieldMetadata(responseData, rangeRowNameMap) {
  let rangeNoteKey = {};
  if (!responseData.sheets) return rangeNoteKey;
  responseData.sheets.forEach((sheetEntry) => {
    let sheetId = sheetEntry.properties.sheetId;
    if (!sheetEntry.data) {
      return;
    }
    sheetEntry.data.forEach((sheetData) => {
      if (!sheetData.rowData) return;
      // prettier-ignore
      const myRangeId = `${sheetData.startRow || 0}:${sheetData.startColumn || 0}`;
      const rangeName = rangeRowNameMap[sheetId][myRangeId];
      sheetData.rowData.forEach((row) => {
        if (!row.values) return;
        row.values.forEach((cell) => {
          if (cell.note) {
            formatHeaderData(
              rangeNoteKey,
              rangeName,
              cell.formattedValue,
              cell.note
            );
          }
        });
      });
    });
  });
  return rangeNoteKey;
}

function rangeFilterHeader(namedRanges, verticalRangeName) {
  const dataFilters = [];
  const rangeRowNameMap = {};
  for (const namedRange of namedRanges) {
    const rangeName = namedRange.name;
    const nr = namedRange.range;
    const sheetId = namedRange.range.sheetId || 0;

    if (!rangeRowNameMap[sheetId]) {
      rangeRowNameMap[sheetId] = {};
    }
    const myRangeId = `${nr.startRowIndex}:${nr.startColumnIndex}`;
    rangeRowNameMap[sheetId][myRangeId] = rangeName;
    // Create a data filter to get only the first row/column (header)
    let gridRange = {
      sheetId: sheetId,
      startRowIndex: nr.startRowIndex,
      startColumnIndex: nr.startColumnIndex,
    };
    if (verticalRangeName.includes(rangeName)) {
      // verticalRange
      gridRange.endRowIndex = nr.endRowIndex;
      gridRange.endColumnIndex = nr.startColumnIndex + 1; // Include only the first column
    } else {
      // horizontalRange
      gridRange.endRowIndex = nr.startRowIndex + 1; // Include only the first row
      gridRange.endColumnIndex = nr.endColumnIndex;
    }
    dataFilters.push({ gridRange: gridRange });
  }
  return [dataFilters, rangeRowNameMap];
}
