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
import { ProjectsClient } from "@google-cloud/resource-manager";
import fs from "fs";
import path from "path";
import yaml from "js-yaml";
import { exec, execSync } from "node:child_process";

export {
  cleanKey,
  lower,
  cleanRes,
  rmBracket,
  isValue,
  sepArray,
  keyValStr,
  sepKeyValPairs,
  lowerObj,
  mergeObjArray,
  mergeAddon,
  readYaml,
  createYaml,
  uploadToGcs,
  readFromGcsPath,
  nestObject,
  writeFile,
  readJson,
  inverseObj,
  underscoreRes,
  toBool,
  toNumber,
  groupAddon,
  customSort,
  parseConfig,
  ssmUri,
  getCurrentTimeFormatted,
  runCommand,
  runCommandSync,
  rpShellVar,
  pascalCase,
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

// replaces $[varName] to '${varName}'
function rpShellVar(str) {
  str = str.replace(/(\$\{[^\}]+\}|\$\([^\)]+\))/gm, `'$1'`);
  str = str.replace(/"\$\[([^\]]+)\]"/gm, `'$\{$1\}'`);
  return str;
}

function trimQuotes(str) {
  if (!str) return str;
  const firstChar = str.charAt(0);
  const lastChar = str.charAt(str.length - 1);
  if (
    (firstChar === '"' && lastChar === '"') ||
    (firstChar === "'" && lastChar === "'")
  ) {
    return str.slice(1, -1);
  }
  return str;
}

function trim(str) {
  if (!str) return str;
  return str.trim();
}

function rmBracket(str, bracket = "()") {
  if (!str) str = "";
  switch (bracket) {
    case "()$":
      return str.replace(/\s*\([^()]*\)\s*$/gm, "").trim();
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

function pascalCase(name) {
  return name
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase())
    .replace(/ /g, "");
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

function readJson(filePath) {
  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    return null;
  }
  try {
    const data = fs.readFileSync(filePath, "utf8");
    return JSON.parse(data);
  } catch (err) {
    console.error(`Error reading or parsing JSON file: ${err}`);
    return null;
  }
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

function keyValStr(str, sep = ":") {
  var re = new RegExp(String.raw`(.+?)${sep}(.+)?`);
  const keyVal = str.match(re);
  let key, val;
  if (keyVal) {
    key = trim(keyVal[1]);
    val = convertType(trim(keyVal[2]));
  } else {
    key = trim(str);
  }
  return [key, val];
}

function sepKeyValPairs(str, sep = ";", forceVal = false, data = {}) {
  if (!str) str = "";
  str = String(str);
  let strArray = sepArray(rmBracket(str, "()$"), sep);
  strArray.forEach((line) => {
    let [key, val] = keyValStr(line, ":");
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

function readYaml(data) {
  const yamlData = yaml.load(data);
  return yamlData;
}

function parseConfig(configData, configType) {
  // Attempt to parse if it's valid yaml/json
  let parsedData;
  if (configType === "yaml") {
    parsedData = readYaml(configData);
  } else if (configType === "json") {
    parsedData = JSON.parse(configData);
  }
  return parsedData;
}

async function uploadToGcs(bucket_name, object_name, contents) {
  const storage = new Storage();
  try {
    await storage.bucket(bucket_name).file(object_name).save(contents);
    console.log(
      `Successfully pushed file ${object_name} to GCS bucket ${bucket_name}`
    );
  } catch (error) {
    console.log("Failed to push file to GCS bucket: " + error);
  }
}

async function readFromGCS(bucketName, fileName) {
  const storage = new Storage();
  const bucket = storage.bucket(bucketName);
  const file = bucket.file(fileName);

  try {
    const [contents] = await file.download();
    return contents.toString(); // Convert Buffer to string
  } catch (error) {
    console.error(`Error reading file from GCS: ${error}`);
    return null; // Or throw the error, depending on your needs
  }
}

async function readFromGcsPath(gcsPath) {
  const match = gcsPath.match(/gs:\/\/([^/]+)\/(.+)/);
  if (match) {
    const bucketName = match[1];
    const objectPath = match[2];
    return await readFromGCS(bucketName, objectPath);
  } else {
    return null;
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

function getCurrentTimeFormatted() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0"); // Months are 0-indexed
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");

  return `${year}-${month}-${day}_${hours}-${minutes}`;
}

async function getProjectIdFromNumber(projectNumber) {
  const client = new ProjectsClient();
  const formattedName = client.projectPath(projectNumber.toString());

  try {
    const [project] = await client.getProject({ name: formattedName });
    return project.projectId;
  } catch (error) {
    console.error("Error getting project ID:", error);
    return null;
  }
}

async function ssmUri(ssmHost, ssmProject, repoName) {
  let gitUri, ssmInstance, ssmProjectNumber, ssmRest, repoUrl;
  if (ssmHost) {
    ssmInstance = ssmHost.split(".")[0];
    ssmProjectNumber = ssmInstance.split("-")[1];
    ssmRest = ssmHost.split(".").slice(1).join(".");
  }
  if (!ssmProject && ssmProjectNumber) {
    ssmProject = await getProjectIdFromNumber(ssmProjectNumber);
  }
  if (ssmInstance) {
    gitUri = `${ssmInstance}-git.${ssmRest}/${ssmProject}/${repoName}.git`;
    repoUrl = `${ssmHost}/${ssmProject}/${repoName}`;
  }
  return [gitUri, repoUrl];
}

function runCommand(command) {
  return exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
    }
    if (stdout) {
      console.log(`stdout: ${stdout}`);
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
    }
    return [stdout, stderr];
  });
}

function runCommandSync(command) {
  let stdout, stderr;
  try {
    const result = execSync(command);
    stdout = result.toString();
  } catch (err) {
    stdout = err.stderr.toString();
    stderr = err.stderr.toString();
  }
  if (stdout) {
    console.log(`stdout: ${stdout}`);
  }
  if (stderr) {
    console.error(`stderr: ${stderr}`);
  }
  return [stdout, stderr];
}
