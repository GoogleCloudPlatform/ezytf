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

import { mergeAddon } from "../util.js";
import { readMapRange } from "../format.js";

export { modifyGke, modifyPrivateGke };

function modifyGke(eztf, resourceRangeMap) {
  const gkeRange = resourceRangeMap["gke"] || "";
  const gkeNodePoolRange = resourceRangeMap["gke_nodepool"] || "";
  let gkeArray = readMapRange(eztf, gkeRange);
  let nodePoolArray = readMapRange(eztf, gkeNodePoolRange);
  let gke = mergeAddon(
    gkeArray,
    nodePoolArray,
    "name",
    "cluster_name",
    "node_pools"
  );
  eztf.eztfConfig[gkeRange] = gke;
}

function modifyPrivateGke(eztf, resourceRangeMap) {
  const gkeRange = resourceRangeMap["gke_private"] || "";
  const gkeNodePoolRange = resourceRangeMap["gke_private_nodepool"] || "";
  let gkeArray = readMapRange(eztf, gkeRange);
  let nodePoolArray = readMapRange(eztf, gkeNodePoolRange);
  let gke = mergeAddon(
    gkeArray,
    nodePoolArray,
    "name",
    "cluster_name",
    "node_pools"
  );
  eztf.eztfConfig[gkeRange] = gke;
}
