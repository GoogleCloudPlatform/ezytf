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
