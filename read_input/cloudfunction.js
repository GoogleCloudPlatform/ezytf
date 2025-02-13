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

/*global process*/
import functions from "@google-cloud/functions-framework";
import { main } from "./main.js";

// make an HTTP request to the deployed function's endpoint.
functions.http("readInputGenerateTF", async (req, res) => {
  try {
    if (req.method !== "POST") {
      return res.status(405).end();
    }
    const configContent = req.body.configContent;
    const ezytfConfigGcsPath = req.body.ezytfConfigGcsPath;
    const configType = req.body.configType || "yaml"; // sheet, yaml, json
    const spreadsheetId = req.body.spreadsheetId;
    const generateCode = req.body.generateCode || false;
    const configBucket =
      req.body.configBucket || process.env.EZTF_CONFIG_BUCKET || "";
    const outputBucket =
      req.body.outputBucket || process.env.EZTF_OUTPUT_BUCKET || "";
    
    let requestLog = { ... req.body };
    if (requestLog.configContent){
      requestLog.configContentProvided = true
      delete requestLog.configContent
    }
    console.log(requestLog);

    if (spreadsheetId || configContent || ezytfConfigGcsPath) {
      let output = await main(
        spreadsheetId,
        configBucket,
        outputBucket,
        generateCode,
        configType,
        configContent,
        ezytfConfigGcsPath
      );
      res.status(200).send(output);
    } else {
      res
        .status(400)
        .send(
          {"error":"Provide either spreadsheetId, configContent or ezytfConfigGcsPath"}
        );
    }
  } catch (error) {
    console.error("Error Generating", error);
    res.status(500).send({"error":`Internal server error ${error}`});
  }
});
