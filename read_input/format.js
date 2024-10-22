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

import {
  lower,
  cleanKey,
  sepArray,
  sepKeyValPairs,
  nestObject,
  rmBracket,
  lowerObj,
  underscoreRes,
  toBool,
  toNumber,
  customSort,
} from "./util.js";
import { mapEntry } from "./resources/custom-map.js";

export {
  flatRanges,
  modifyGeneric,
  getTfRanges,
  mapTfRanges,
  readMapRange,
  readNamedRange,
  setRangeDataByName,
  formatHeaderData,
};

function readMapRange(eztf, rangeName) {
  let resource = eztf.rangeResourceTfMap[rangeName] || rangeName;
  let [headers, rangeValue] = readNamedRange(eztf, rangeName);
  return mapData(eztf, headers, rangeValue, rangeName, resource);
}


function mapData(eztf, headers, values, range, resource) {
  const data = values
    .map((row) => {
      const obj = {};
      // row = row.map(str => String(str).trim());
      if (row.every((str) => !str)) {
        return {};
      }
      headers.forEach((header, index) => {
        obj[header] = row[index];
      });

      let newObj = mapGeneric(eztf.rangeNoteKey, range, obj);
      if (mapEntry[resource] && !!newObj && Object.keys(newObj).length > 0) {
        newObj = mapEntry[resource](newObj, eztf);
      }
      return newObj;
    })
    .filter((obj) => !!obj && Object.keys(obj).length > 0);
  // console.log(JSON.stringify(data,null,2));
  if (mapEntry[resource]) {
    console.log("Custom Map:", resource, range);
  }
  return data;
}

function getRangeByName(eztf, rangeName) {
  return eztf.readRanges[rangeName];
}

function setRangeDataByName(eztf, rangeName, data) {
  eztf.readRanges[rangeName] = data;
}

function readNamedRange(eztf, rangeName) {
  var values = getRangeByName(eztf, rangeName);
  if (!values) {
    return [[], []];
  }
  const keyMap = eztf.rangeNoteKey?.[rangeName]?.key || {};
  let headers = values[0];
  let rangeValue = values.slice(1);
  let newheaders = headers.map((key) => {
    key = cleanKey(key);
    return keyMap[key] || key;
  });
  // console.log(rangeName, newheaders, rangeValue)
  return [newheaders, rangeValue];
}

function mapVariable(data) {
  for (const [key, value] of Object.entries(data)) {
    data[key] = value[0];
  }
  return data;
}

function getTfRanges(eztf, rangeName) {
  const [tfRanges, verticalRangesList] = groupTfRanges(
    readMapRange(eztf, rangeName)
  );
  eztf.rangeResourceTfMap = Object.assign(
    {},
    ...Object.values(tfRanges).flat(2)
  );
  return [tfRanges, verticalRangesList];
}

function mapTfRanges(data) {
  if (!data.enabled || !data.stack || !data.resource) {
    return {};
  }
  const resources = sepKeyValPairs(data.resource, ",", "key", []);
  const [verticalRange, ranges] = checkVerticalRange(resources);
  data.resource = ranges;
  data.vertical = verticalRange;
  return data;
}

function checkVerticalRange(input) {
  const vertical = [];
  const output = input.map((item) => {
    const newItem = {};
    for (const [key, val] of Object.entries(item)) {
      const newKey = rmBracket(key, "[]");
      const newval = rmBracket(val, "[]");
      newItem[newKey] = newval;
      if (
        val.match(/\[\s*(?:v|vertical)\s*\]/) ||
        key.match(/\[\s*(?:v|vertical)\s*\]/)
      ) {
        vertical.push(newKey);
      }
    }
    return newItem;
  });
  return [vertical, output];
}

function groupTfRanges(res) {
  const verticalRangesList = [];
  const groupRanges = res.reduce((tfrange, row) => {
    if (!tfrange[row.stack]) {
      tfrange[row.stack] = [];
    }
    tfrange[row.stack].push(row.resource);
    verticalRangesList.push(...row.vertical);
    return tfrange;
  }, {});
  return [groupRanges, verticalRangesList];
}

function flatRanges(tfRanges) {
  let newRange = {};
  for (var key in tfRanges) {
    newRange[key] = tfRanges[key].flat();
  }
  return newRange;
}

function modifyGeneric(eztf, rangeResource) {
  eztf.eztfConfig[rangeResource] = readMapRange(eztf, rangeResource);
}

// allow_empty_keys
// required_keys
function getRangeSpecificKeys(rangeNoteKey, rangeResource, key) {
  if (!rangeNoteKey[rangeResource]) {
    return [];
  }
  if (!rangeNoteKey[rangeResource][key]) {
    return [];
  }
  return rangeNoteKey[rangeResource][key];
}

function checkRequired(data, requiredKeys) {
  for (const key of requiredKeys) {
    if (data[key] === "" || data[key] === undefined || data[key] === null) {
      return false;
    }
  }
  return true;
}

function deleteEmpty(data, allowEmpty) {
  for (const [key, value] of Object.entries(data)) {
    if (value === "" || value === undefined || value === null) {
      if (allowEmpty.includes(key)) {
        data[key] = "";
      } else {
        delete data[key];
      }
    }
  }
}

function replaceVariables(input, variables) {
  return input.replace(/{([^}]+)}/g, (match, variableName) => {
    return variables[variableName] || match;
  });
}

function metadataFunSwitch(metadata, data, key) {
  if (metadata === "commaseperated") {
    data[key] = sepArray(data[key]);
  } else if (metadata === "semicolonseperated") {
    data[key] = sepArray(data[key], ";");
  } else if (metadata.startsWith("dontallowif_")) {
    let val = metadata.split("_")[1] || "";
    if (lower(data[key]) === lower(val)) {
      delete data[key];
    }
  } else if (metadata.startsWith("dontkeep")) {
    delete data[key];
  } else if (metadata === "string") {
    data[key] = String(data[key]);
  } else if (metadata === "bool") {
    data[key] = toBool(data[key]);
  } else if (metadata === "number") {
    data[key] = toNumber(data[key]);
  } else if (metadata === "upper") {
    data[key] = lower(data[key]).toUpperCase();
  } else if (metadata === "lower") {
    data[key] = lower(data[key]);
  } else if (metadata === "underscore") {
    data[key] = underscoreRes(data[key]);
  } else if (metadata === "keyvalpair") {
    data[key] = sepKeyValPairs(data[key], ";", true);
  } else if (metadata === "templatekey") {
    const newKey = replaceVariables(key, data);
    data[newKey] = data[key];
    if (key !== newKey) {
      delete data[key];
    }
  } else if (metadata === "moduleid") {
    data["_eztf_module_id"] = data[key];
  }
}

const metadataOrderMap = {
  string: 0,
  bool: 0,
  number: 0,
  underscore: 1,
  upper: 1,
  lower: 1,
  commaseperated: 2,
  semicolonseperated: 2,
  keyvalpair: 2,
  templatekey: 3,
  dontallowif_: 4,
  dontkeep: 4,
};

function runMetadataFun(metadataObj, data, skip = [], only = []) {
  for (const [key, metadataFun] of Object.entries(metadataObj)) {
    for (const fun of metadataFun) {
      if (
        !Object.prototype.hasOwnProperty.call(data, key) ||
        skip.includes(fun) ||
        (only.length > 0 && !only.includes(fun))
      ) {
        continue;
      }
      metadataFunSwitch(fun, data, key);
    }
  }
}

function mapGeneric(rangeNoteKey, rangeResource, data) {
  const requiredKeys = rangeNoteKey?.[rangeResource]?.required_keys || [];
  const allowEmptyKeys = rangeNoteKey?.[rangeResource]?.allow_empty_keys || [];

  if (!checkRequired(data, requiredKeys)) {
    return {};
  }
  let metadataObj = rangeNoteKey?.[rangeResource]?.metadata || {};
  deleteEmpty(data, allowEmptyKeys);
  // skip dontkeep to preserve templating key data in first iteration
  runMetadataFun(metadataObj, data, ["dontkeep"], []);
  // only apply dontkeep if present
  runMetadataFun(metadataObj, data, [], ["dontkeep"]);
  return nestObject(data);
}

function formatHeaderData(rangeNoteKey, rangeName, header, note) {
  if (!rangeNoteKey[rangeName]) {
    rangeNoteKey[rangeName] = {
      key: {},
      required_keys: [],
      allow_empty_keys: [],
      metadata: {},
      module: {},
    };
  }
  let headerKey = cleanKey(header);
  let noteHeader = lowerObj(sepKeyValPairs(note), true);

  if (noteHeader["field"]) {
    rangeNoteKey[rangeName]["key"][headerKey] = noteHeader["field"];
    headerKey = noteHeader["field"];
  }
  if (noteHeader.metadata) {
    let keyMetadata = sepArray(noteHeader["metadata"].toLowerCase());
    if (keyMetadata.includes("required"))
      rangeNoteKey[rangeName]["required_keys"].push(headerKey);
    if (keyMetadata.includes("allowempty"))
      rangeNoteKey[rangeName]["allow_empty_keys"].push(headerKey);
    keyMetadata = keyMetadata.filter(
      (val) => !["required", "allowempty"].includes(val)
    );
    if (keyMetadata.length > 0) {
      let sortedKeyMatadata = customSort(keyMetadata, metadataOrderMap);
      rangeNoteKey[rangeName]["metadata"][headerKey] = sortedKeyMatadata;
    }
  }
  if (noteHeader.source) {
    rangeNoteKey[rangeName]["module"]["source"] = noteHeader["source"];
  }
  if (noteHeader.version) {
    rangeNoteKey[rangeName]["module"]["version"] = noteHeader["version"];
  }
}
