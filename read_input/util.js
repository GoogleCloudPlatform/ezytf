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

import { Storage } from "@google-cloud/storage";
import fs from "fs";
import path from "path";
import yaml from "js-yaml";

export {
  cleanKey,
  lower,
  cleanRes,
  rmBracket,
  isValue,
  sepArray,
  sepKeyValPairs,
  lowerObj,
  mergeObjArray,
  mergeAddon,
  createYaml,
  uploadToGcs,
  nestObject,
  writeFile,
  inverseObj,
  underscoreRes,
  toBool,
  toNumber,
  groupAddon,
  customSort,
};

function cleanKey(str) {
  if (!str) str = "";
  return lower(sepArray(str, ":").join("."));
}

function lower(str) {
  if (!str) str = "";
  return rpSpaces(rmBracket(str)).toLowerCase();
}

function underscoreRes(str) {
  if (!str) str = "";
  return str.trim().replace(/\./g, "_").replace(/-/g, "_").toLowerCase();
}

function rpSpaces(str) {
  if (!str) str = "";
  return str.trim().replace(/\s+/g, "_");
}

function cleanRes(str) {
  if (!str) str = "";
  return str.trim().replace(/\./g, "-").replace(/_/g, "-").toLowerCase();
}

function trimQuotes(str) {
  if (!str) return str;
  return str.replace(/^['"]+|['"]+$/g, "");
}

function rmBracket(str, bracket = "()") {
  if (!str) str = "";
  switch (bracket) {
    case "()":
      return str.replace(/\s*\(.*\)/, "").trim();
    case "[]":
      return str.replace(/\s*\[.*\]/, "").trim();
    case "{}":
      return str.replace(/\s*\{.*\}/, "").trim();
    default:
      return str;
  }
}

function isValue(str, value) {
  return lower(str) === value ? true : false;
}

function sepArray(str, sep = ",") {
  if (!str) str = "";
  str = String(str);
  return str
    .split(sep)
    .map((value) => value.trim())
    .filter((value) => value);
}

function writeFile(filePath, data) {
  var dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(filePath, data);
}

function toNumber(val) {
  let newVal = String(val).trim();
  if (!isNaN(newVal)) {
    return Number(newVal);
  }
  return val;
}

function toBool(val) {
  let newVal = String(val).trim().toLowerCase();
  if (newVal === "true") {
    return true;
  } else if (newVal === "false") {
    return false;
  }
  return val;
}

function convertType(str) {
  if (!isNaN(str)) {
    return Number(str);
  } else if (str === "true") {
    return true;
  } else if (str === "false") {
    return false;
  } else if (str === '""' || str === "''") {
    return "";
  }
  return trimQuotes(str);
}

function sepKeyValPairs(str, sep = ";", forceVal = false, data = {}) {
  if (!str) str = "";
  str = String(str);
  let strArray = sepArray(rmBracket(str), sep);
  strArray.forEach((line) => {
    let keyVal = sepArray(line, ":");
    let key = keyVal[0];
    let val = convertType(keyVal[1]);
    if (forceVal && (val === null || val === undefined)) {
      if (forceVal === "key") {
        val = val || key || "";
      } else {
        val = val || "";
      }
    }
    if (Array.isArray(data)) {
      let d = {};
      d[key] = val;
      data.push(d);
    } else if (typeof data === "object" && data !== null) {
      data[key] = val;
    }
  });
  return data;
}

function inverseObj(obj) {
  var invObj = {};
  for (var key in obj) {
    invObj[obj[key]] = key;
  }
  return invObj;
}

function lowerObj(obj, onKey = false, onValue = false) {
  const lowerCaseObj = Object.keys(obj).reduce((acc, key) => {
    let modifyKey = key;
    let modifyValue = obj[key];
    if (onKey) modifyKey = key.toLowerCase();
    if (onValue)
      modifyValue =
        typeof obj[key] === "string" ? obj[key].toLowerCase() : obj[key];
    acc[modifyKey] = modifyValue;
    return acc;
  }, {});
  return lowerCaseObj;
}

function mergeObjArray(arr1, arr2, name) {
  return [...arr1, ...arr2].reduce((acc, obj) => {
    if (acc[obj[name]]) {
      acc[obj[name]] = { ...acc[obj[name]], ...obj }; // Merge properties
    } else {
      acc[obj[name]] = obj;
    }
    return acc;
  }, {});
}

function mergeAddon(data, subdata, dataMergeKey, subdataMergeKey, addonKey) {
  const result = data.map((item) => {
    const addon = subdata
      .filter((subItem) => subItem[subdataMergeKey] === item[dataMergeKey])
      .map((subItem) => {
        let copyItem = { ...subItem };
        delete copyItem[subdataMergeKey];
        return copyItem;
      });
    const mergeData = { ...item };
    mergeData[addonKey] = addon;
    return mergeData;
  });
  return result;
}

function groupAddon(dataArray, groupkey, arrayKey) {
  const result = dataArray.reduce((acc, obj) => {
    if (!acc[obj[groupkey]]) {
      let myObj = { ...obj };
      delete myObj[arrayKey];
      acc[obj[groupkey]] = myObj;
      acc[obj[groupkey]][arrayKey] = [];
    }
    if (obj[arrayKey]) {
      let myAdd = { ...obj[arrayKey] };
      acc[obj[groupkey]][arrayKey].push(myAdd);
    }
    return acc;
  }, {});
  return result;
}

function createYaml(data) {
  const yamlString = yaml.dump(data);
  return yamlString;
}

async function uploadToGcs(bucket_name, object_name, contents) {
  const storage = new Storage();
  try {
    await storage
      .bucket(bucket_name)
      .file(object_name)
      .save(contents);
    console.log(
      `Successfully pushed file ${object_name} to GCS bucket ${bucket_name}`
    );
  } catch (error) {
    console.log("Failed to push file to GCS bucket: " + error);
  }
}

function nestObject(flatObject, delimiter = ".") {
  const nestedObject = {};

  for (const flatKey in flatObject) {
    // splits by delimiter escapes delimiter in quotes
    var re = new RegExp(
      String.raw`(?:[^${delimiter}"']+|['"][^'"]*["'])+`,
      "g"
    );
    // const keys = flatKey.match(/(?:[^\."']+|['"][^'"]*["'])+/g);
    const keys = flatKey.match(re);
    let currentLevel = nestedObject;
    let lastKeyIndex = keys.length - 1;

    for (let i = 0; i < keys.length; i++) {
      // trim "" quoted key
      const key = trimQuotes(keys[i]);
      // matches [0][1][2] in key
      const arrayMatch = key.match(/^(.+?)\[(.+)\]$/);
      if (arrayMatch) {
        const arrayKey = arrayMatch[1];
        const arrayIndices = arrayMatch[2].split("][").map(Number);

        currentLevel[arrayKey] = currentLevel[arrayKey] || [];
        let currentArray = currentLevel[arrayKey];

        for (let j in arrayIndices) {
          var arrayIndex = arrayIndices[j];
          while (currentArray.length < arrayIndex) {
            currentArray.push(null);
          }
          // skip last nested array
          if (j < arrayIndices.length - 1) {
            currentArray[arrayIndex] = currentArray[arrayIndex] || [];
            currentArray = currentArray[arrayIndex];
          }
        }
        // assign data at last nested array
        if (i === lastKeyIndex) {
          currentArray[arrayIndex] = flatObject[flatKey];
        } else {
          // If NOT last key in path, ensure array element is an object
          currentArray[arrayIndex] = currentArray[arrayIndex] || {};
          currentLevel = currentArray[arrayIndex];
        }
      } else {
        // Handle object keys normally
        if (i === lastKeyIndex) {
          currentLevel[key] = flatObject[flatKey];
        } else {
          currentLevel[key] = currentLevel[key] || {};
          currentLevel = currentLevel[key];
        }
      }
    }
  }
  return nestedObject;
}

function customSort(arr, orderMap) {
  arr.sort((a, b) => {
    const indexA = orderMap[a];
    const indexB = orderMap[b];

    // Handle cases where elements are not in the custom order
    if (indexA === undefined && indexB === undefined) {
      // If both elements are not in the orderlist, keep as it is
      return 0;
    } else if (indexA === undefined) {
      // If a is not in the orderlist, place it after b
      return 1;
    } else if (indexB === undefined) {
      // If b is not in the orderlist, place it after a
      return -1;
    } else {
      // If both elements are in the order, sort by their indices
      return indexA - indexB;
    }
  });
  return arr;
}