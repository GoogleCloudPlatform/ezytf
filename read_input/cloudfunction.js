/*global process*/
import functions from "@google-cloud/functions-framework";
import { main } from "./main.js";

// make an HTTP request to the deployed function's endpoint.
functions.http("readInputGenerateTF", async (req, res) => {
  try {
    if (req.method !== "POST") {
      return res.status(405).end();
    }
    const spreadsheetId = req.body.spreadsheetId;
    const generateCode = req.body.generateCode || false;
    const configBucket =
      req.body.configBucket || process.env.EZTF_CONFIG_BUCKET || "";
    if (req.body.outputBucket) {
      process.env.EZTF_OUTPUT_BUCKET = req.body.outputBucket;
    }
    console.log(req.body)
    if (!spreadsheetId) {
      return res.status(400).send("Missing spreadsheetId parameter");
    }

    await main(spreadsheetId, configBucket, generateCode);
    res.status(200).send("config generation started");
  } catch (error) {
    console.error("Error Generating", error);
    res.status(500).send("Internal server error");
  }
});
