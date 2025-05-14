/**
 * Copyright 2025 Google LLC
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

import { readMapRange } from "../format.js";

export { modifyJsonYaml, modifyCurl, modifyVariable };

function modifyJsonYaml(eztf, resourceRangeMap) {
  for (let res of ["json", "yaml"]) {
    const configRange = resourceRangeMap[res] || "";
    if (configRange) {
      let configArray = readMapRange(eztf, configRange);
      let configData = configArray;
      let format = eztf.rangeNoteKey?.[configRange]?.format || "";
      if (format === "mapcombine") {
        configData = [configArray.reduce((acc, obj) => {
          return { ...acc, ...obj };
        }, {})];
      } else if (format === "combine"){
        configData = [configArray]
      }
      eztf.eztfConfig[configRange] = configData;
    }
  }
}

function modifyCurl(eztf, resourceRangeMap) {
  const curlRange = resourceRangeMap["curl"] || "";
  if (curlRange) {
    let curlArray = readMapRange(eztf, curlRange);
    let curlData = curlArray;
    let format = eztf.rangeNoteKey?.[curlRange]?.format || "";
    if (format === "combine"){
      curlData = [curlArray]
    }
    eztf.eztfConfig[curlRange] = curlData;
  }
}

function modifyVariable(eztf, resourceRangeMap) {
  const varRange = resourceRangeMap["variable"] || "";
  let varData = readMapRange(eztf, varRange)[0] || {};
  eztf.eztfConfig[varRange] = varData;
}