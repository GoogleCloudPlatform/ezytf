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

export { modifyPerimeter, fixScPolicies };

function modifyPerimeter(eztf, resourceRangeMap) {
  const perimeterRange = resourceRangeMap["sc_perimeter"] || "";
  const ingressEgressRange = resourceRangeMap["sc_ingress_egress"] || "";
  let perimeterArray = readMapRange(eztf, perimeterRange);
  let ingressEgressArray = readMapRange(eztf, ingressEgressRange);
  let policies = groupScPolicies(ingressEgressArray);
  let perimeter = mergeAddon(
    perimeterArray,
    policies.ingress_policies,
    "perimeter_name",
    "perimeter_name",
    "ingress_policies"
  );
  perimeter = mergeAddon(
    perimeter,
    policies.egress_policies,
    "perimeter_name",
    "perimeter_name",
    "egress_policies"
  );
  eztf.eztfConfig[perimeterRange] = perimeter;
}

function fixScPolicies(data) {
  if (data?.to?.operations?.service_name) {
    const service_name = data.to.operations.service_name;
    data.to.operations[service_name] = {};
    delete data.to.operations.service_name;
    ["method", "permission"].forEach((operation_type) => {
      if (data.to.operations[operation_type]) {
        data.to.operations[service_name][operation_type] =
          data.to.operations[operation_type];
        delete data.to.operations[operation_type];
      }
    });
    if (service_name === "egress_policies" && data?.from?.sources) {
      delete data.from.sources;
    }
  }
  return data;
}

function groupScPolicies(ingressEgressArray) {
  let policies = { ingress_policies: new Map(), egress_policies: new Map() };
  ingressEgressArray.forEach((data) => {
    const policy_type = data.policy_type;
    delete data.policy_type;
    const uni = JSON.stringify({
      perimeter_name: data.perimeter_name,
      from: data.from,
      to: { resources: data.to.resources },
    });
    if (policies[policy_type][uni]) {
      if (data?.to?.operations) {
        policies[policy_type][uni].to.operations = {
          ...policies[policy_type][uni].to.operations,
          ...data.to.operations,
        };
      }
    } else {
      policies[policy_type][uni] = data;
    }
  });
  policies.ingress_policies = Object.values(policies.ingress_policies);
  policies.egress_policies = Object.values(policies.egress_policies);
  return policies;
}

// use below function instead of groupScPolicies if you don't want to group to operations
function splitScPolicies(ingressEgressArray) {
  let policies = { ingress_policies: [], egress_policies: [] };
  ingressEgressArray.forEach((data) => {
    const policy_type = data.policy_type;
    delete data.policy_type;
    policies[policy_type].push(data);
  });
  return policies;
}

/*
ingress egress desired schema
{ from={  identities=[], identity_type="ID_TYPE" sources={ resources=[], access_levels=[] }, }, to={ resources=[], operations={ "SRV_NAME"={ OP_TYPE=[] }}}}]

// below in ingress policies only
from { sources={ resources=[], access_levels=[] }}
*/
