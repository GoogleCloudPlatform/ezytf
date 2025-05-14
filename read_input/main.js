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
import { modifyResource } from "./resources/custom-map.js";
import { readSheetRanges } from "./read/google-sheet-read.js";
import { readMapRange, flatRanges, modifyGeneric, supportedTfstacks } from "./format.js";
import {
  createYaml,
  cleanRes,
  uploadToGcs,
  readFromGcsPath,
  parseConfig,
  writeFile,
  inverseObj,
  ssmUri,
  getCurrentTimeFormatted,
  readJson,
  runCommand,
  runCommandSync,
} from "./util.js";

export { main };

const LOCAL_CONFIG_DIR =
  process.env.EZTF_CONFIG_DIR || "../ezytf-gen-data/eztf-config";

const LOCAL_OUTPUT_DIR =
  process.env.EZTF_OUTPUT_DIR || "../ezytf-gen-data/eztf-output";

const EZTF_SUPPORTED_TF_FILE = "../generate/supported_tf.json";

process.env.CI = 1;

const supportedTf = new Set(readJson(EZTF_SUPPORTED_TF_FILE));

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
  eztf.eztfConfig["eztf"] = {
    tf_any_module: {},
    tf_any_data: {},
    tf_any_resource: {},
    tf_stacks: []
  };
  let stacks = flatRanges(tfRanges)
  eztf.eztfConfig["eztf"]["stacks"] = stacks;
  eztf.eztfConfig["eztf"]["tf_stacks"] = supportedTfstacks(stacks, supportedTf)

  for (const stack of Object.values(tfRanges)) {
    for (const rangeResourceObjArray of stack) {
      const resourceRangeObj = inverseObj(
        Object.assign({}, ...rangeResourceObjArray)
      );
      const resource = Object.keys(resourceRangeObj)[0];
      const range = resourceRangeObj[resource];
      if (resource === "any_module" || resource === "mod") {
        eztf.eztfConfig["eztf"]["tf_any_module"][range] =
          eztf.rangeNoteKey?.[range]?.["tf_module"] || {};
      }
      if (resource === "any_data" || resource === "data") {
        eztf.eztfConfig["eztf"]["tf_any_data"][range] =
          eztf.rangeNoteKey?.[range]?.["tf_data"] || {};
      }
      if (resource === "any_resource" || resource === "res") {
        eztf.eztfConfig["eztf"]["tf_any_resource"][range] =
          eztf.rangeNoteKey?.[range]?.["tf_resource"] || {};
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
}

async function getEzytfOutputDetails(repoName, gitUri, outputBucket) {
  let output = { error: "" };
  let repoUrl;
  if (!gitUri) {
    [gitUri, repoUrl] = await ssmUri(
      process.env.EZTF_SSM_HOST,
      process.env.EZTF_SSM_PROJECT,
      repoName
    );
  } else if (gitUri.endsWith(".git")){
    repoUrl = gitUri.slice(0, -4);
    // remove -git ssm git uri
    repoUrl = repoUrl.replace(/-git(?=\..+\.sourcemanager\.dev)/, "");
  }
  if (outputBucket) {
    let ezytfTime = getCurrentTimeFormatted();
    let gcs_prefix = `eztf-output/${repoName}/${repoName}-${ezytfTime}/`;
    output["output_gcs"] = `gs://${outputBucket}/${gcs_prefix}`;
    output["output_gcs_prefix"] = gcs_prefix;
  }
  if (repoUrl) {
    output["repo_url"] = repoUrl;
  }
  if (gitUri) {
    output["git_uri"] = gitUri;
  }
  return output;
}

async function getEzytfConfigDetails(eztfConfig, outputBucket = "") {
  let configName = eztfConfig["variable"]["ez_config_name"] || "ezy";
  let gitUri = eztfConfig["variable"]["ez_repo_git_uri"];
  let customerName = cleanRes(eztfConfig["variable"]["domain"]);
  let repoName = `gcp-${customerName}-${configName}`;
  let fileName = `${configName}/${repoName}.yaml`;
  let output = await getEzytfOutputDetails(repoName, gitUri, outputBucket);
  let isTfstack = true;
  if (supportedTf.size > 0){
    isTfstack = eztfConfig["eztf"]["tf_stacks"].length > 0;
  }
  
  return [fileName, repoName, output, isTfstack];
}

function writeEztfConfig(eztfConfig, configBucket, fileName) {
  let configYaml = createYaml(eztfConfig);
  console.log(`configBucket: ${configBucket}`);
  let eztfInputConfig;

  if (configBucket) {
    eztfInputConfig = `eztf-config/${fileName}`;
    uploadToGcs(configBucket, eztfInputConfig, configYaml);
  } else {
    eztfInputConfig = `${LOCAL_CONFIG_DIR}/${fileName}`;
    writeFile(eztfInputConfig, configYaml);
  }
  console.log(`ezyTF yaml config generated, ${eztfInputConfig}`);
  return eztfInputConfig;
}

async function generateTF(
  eztfInputConfigFile,
  customer,
  configBucket = "",
  outputBucket = "",
  outputGcsPrefix = "",
  asyncGenerate = false,
  anyTfStack = true
) {
  console.log("running code generation");

  let generateScript = `export EZTF_INPUT_CONFIG=${eztfInputConfigFile} && \
    export EZTF_IS_TF=${anyTfStack} && \
    export EZTF_CDK_OUTPUT_DIR=${customer} && \
    export EZTF_OUTPUT_DIR=${LOCAL_OUTPUT_DIR} && \
    export EZTF_CONFIG_BUCKET=${configBucket} && \
    export EZTF_OUTPUT_BUCKET=${outputBucket} && \
    export EZTF_OUTPUT_GCS_PREFIX=${outputGcsPrefix} && \
    if [ -f "\${EZTF_ACCESS_TOKEN_FILE}" ]; then gcloud config set auth/access_token_file $EZTF_ACCESS_TOKEN_FILE 2>/dev/null ; fi && \
    cd ../generate && \
    
    if [ "\${EZTF_IS_TF}" = "true" ]; then cdktf synth --hcl --output $EZTF_CDK_OUTPUT_DIR >/dev/null ; fi && \
    python -W ignore repo.py`;
  // console.log(generateScript)
  if (asyncGenerate) {
    runCommand(generateScript);
  } else {
    return runCommandSync(generateScript);
  }
  return [null, null];
}

async function main(
  spreadsheetId = "",
  configBucket = "",
  outputBucket = "",
  generateCode = false,
  configType = "yaml",
  configContent = "",
  ezytfConfigGcsPath = "",
  asyncGenerate = false
) {
  let eztfConfig;
  let eztfInputConfigFile;
  if (spreadsheetId) {
    let eztf = new Eztf();
    const tfRanges = await readSheetRanges(eztf, spreadsheetId);
    logInfo(eztf);
    generateEztfConfig(eztf, tfRanges);
    eztfConfig = eztf.eztfConfig;
  } else if (configContent) {
    let configData = Buffer.from(configContent, "base64").toString();
    eztfConfig = parseConfig(configData, configType);
  } else if (ezytfConfigGcsPath) {
    let configData = await readFromGcsPath(ezytfConfigGcsPath);
    eztfConfig = parseConfig(configData, configType);
  }
  let [fileName, repoName, outputDetails, isTfstack] = await getEzytfConfigDetails(
    eztfConfig,
    outputBucket
  );
  eztfInputConfigFile = writeEztfConfig(eztfConfig, configBucket, fileName);
  let outputGcsPrefix = outputDetails["output_gcs_prefix"];
  if (generateCode) {
    let [eztfout, eztferr] = await generateTF(
      eztfInputConfigFile,
      repoName,
      configBucket,
      outputBucket,
      outputGcsPrefix,
      asyncGenerate,
      isTfstack
    );
    if (eztfout) {
      outputDetails["log"] = eztfout;
    }
    if (eztferr) {
      outputDetails["error"] = eztferr;
    }
  }
  delete outputDetails["output_gcs_prefix"];
  return outputDetails;
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
        "",
        false
      );
    } else if (mode === "generate") {
      await main(
        process.env.EZTF_SHEET_ID,
        process.env.EZTF_CONFIG_BUCKET,
        process.env.EZTF_OUTPUT_BUCKET,
        true
      );
    }
  }
}
