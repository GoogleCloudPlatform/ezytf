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

/*global  process*/
import * as url from "node:url";
import { exec } from "child_process";
import { modifyResource } from "./resources/custom-map.js";
import { readSheetRanges } from "./read/google-sheet-read.js";
import { readMapRange, flatRanges, modifyGeneric } from "./format.js";
import {
  createYaml,
  cleanRes,
  uploadToGcs,
  writeFile,
  inverseObj,
} from "./util.js";

export { main };

const LOCAL_CONFIG_DIR =
  process.env.EZTF_CONFIG_DIR || "../ezytf-gen-data/eztf-config";

class Eztf {
  constructor() {
    this.readRanges = {};
    this.eztfConfig = {};
    this.rangeNoteKey = {};
    this.rangeResourceTfMap = {};
  }
}

function generateEztfConfig(eztf, tfRanges) {
  console.log("starting ezyTF yaml config generation");

  let variable = readMapRange(eztf, "variable")[0] || {};

  eztf.eztfConfig["variable"] = variable;
  eztf.eztfConfig["eztf"] = { tf_any_module: {} };
  eztf.eztfConfig["eztf"]["stacks"] = flatRanges(tfRanges);

  for (const stack of Object.values(tfRanges)) {
    for (const rangeResourceObjArray of stack) {
      const resourceRangeObj = inverseObj(
        Object.assign({}, ...rangeResourceObjArray)
      );
      const resource = Object.keys(resourceRangeObj)[0];
      const range = resourceRangeObj[resource];
      if (resource === "any_module") {
        eztf.eztfConfig["eztf"]["tf_any_module"][range] =
          eztf.rangeNoteKey?.[range]?.["module"] || {};
      }
      if (Object.prototype.hasOwnProperty.call(modifyResource, resource)) {
        console.log("Custom Modify: ", Object.values(resourceRangeObj).join());
        modifyResource[resource](eztf, resourceRangeObj);
      } else {
        console.log("Generic Modify:", range);
        modifyGeneric(eztf, range);
      }
    }
  }
  let configYaml = createYaml(eztf.eztfConfig);
  // console.log(configYaml);
  return configYaml;
}

function writeEztfConfig(eztf, configYaml, configBucket) {
  console.log(`configBucket: ${configBucket}`);
  let configName = eztf.eztfConfig["variable"]["eztf_config_name"] || "ezytf";

  let customerName = cleanRes(eztf.eztfConfig["variable"]["domain"]);
  let customer = `gcp-${customerName}-${configName}`;
  let fileName = `${configName}/${customer}.yaml`;
  let eztfInputConfig = fileName;

  if (configBucket) {
    eztfInputConfig = `eztf-config/${fileName}`;
    uploadToGcs(configBucket, eztfInputConfig, configYaml);
  } else {
    eztfInputConfig = `${LOCAL_CONFIG_DIR}/${fileName}`;
    writeFile(eztfInputConfig, configYaml);
  }
  console.log(`ezyTF yaml config generated, ${eztfInputConfig}`);
  return [eztfInputConfig, customer];
}

function generateTF(eztfInputConfig, customer) {
  process.env.EZTF_INPUT_CONFIG = eztfInputConfig;
  process.env.EZTF_CDK_OUTPUT_DIR = customer;
  process.env.EZTF_OUTPUT_DIR =
    process.env.EZTF_OUTPUT_DIR || "../ezytf-gen-data/eztf-output";
  process.env.CI = 1;

  exec(
    `echo $EZTF_INPUT_CONFIG && \
    echo $EZTF_CDK_OUTPUT_DIR && \
    if [ -f "\${EZTF_ACCESS_TOKEN_FILE}" ]; then gcloud config set auth/access_token_file $EZTF_ACCESS_TOKEN_FILE ; fi && \
    cd ../generate && pwd && \
    
    cdktf synth --hcl --output $EZTF_CDK_OUTPUT_DIR && \
    python -W ignore repo.py`,
    (err, stdout, stderr) => {
      console.log(`stdout: ${stdout}`);
      console.log(`stderr: ${stderr}`);
      if (err) {
        console.error(err);
        return;
      }
    }
  );
}

async function main(spreadsheetId, configBucket = "", generateCode = false) {
  let eztf = new Eztf();
  const tfRanges = await readSheetRanges(eztf, spreadsheetId);
  logInfo(eztf);
  const configYaml = generateEztfConfig(eztf, tfRanges);

  let [eztfInputConfig, customer] = writeEztfConfig(
    eztf,
    configYaml,
    configBucket
  );
  if (generateCode) {
    console.log("running cdktf synth");
    generateTF(eztfInputConfig, customer);
  }
}

function logInfo(eztf) {
  // console.log(JSON.stringify(global.readRanges,null,2))
  // console.log(JSON.stringify(global.rangeNoteKey, null, 2));
  const usedMetadata = new Set();
  for (const noteRangeValues of Object.values(eztf.rangeNoteKey)) {
    for (const metadataFun of Object.values(noteRangeValues["metadata"])) {
      metadataFun.forEach((item) => usedMetadata.add(item));
    }
  }
  console.log("user used metadata:", usedMetadata);
}

// below code will run during node main.js
if (import.meta.url.startsWith("file:")) {
  const modulePath = url.fileURLToPath(import.meta.url);
  if (process.argv[1] === modulePath) {
    let mode = process.argv[2];
    if (mode === "read") {
      await main(
        process.env.EZTF_SHEET_ID,
        process.env.EZTF_CONFIG_BUCKET,
        false
      );
    } else if (mode === "generate") {
      await main(
        process.env.EZTF_SHEET_ID,
        process.env.EZTF_CONFIG_BUCKET,
        true
      );
    }
  }
}
