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

import { lower, rmBracket, sepArray, rpShellVar, pascalCase } from "../util.js";

export {
  fixGroup,
  fixLogging,
  fixProject,
  fixFirewall,
  fixIam,
  fixVpnHa,
  fixTunnel,
  fixJsonYamlMap,
  fixVariable,
  fixAgentspaceConnector,
};

const defaultSetupApis = [
  "serviceusage.googleapis.com",
  "cloudresourcemanager.googleapis.com",
  "cloudbilling.googleapis.com",
  "iam.googleapis.com",
  "admin.googleapis.com",
  "storage-api.googleapis.com",
  "logging.googleapis.com",
  "monitoring.googleapis.com",
  "orgpolicy.googleapis.com",
  "cloudidentity.googleapis.com",
];

const defaultSetupRoles = [
  "roles/resourcemanager.organizationAdmin",
  "roles/orgpolicy.policyAdmin",
  "roles/iam.organizationRoleAdmin",
  "roles/resourcemanager.folderAdmin",
  "roles/resourcemanager.folderIamAdmin",
  "roles/resourcemanager.projectCreator",
  "roles/securitycenter.admin",
  "roles/compute.networkAdmin",
  "roles/compute.xpnAdmin",
  "roles/compute.securityAdmin",
  "roles/iam.serviceAccountCreator",
  "roles/logging.admin",
  "roles/monitoring.admin",
  "roles/pubsub.admin",
  "roles/bigquery.admin",
  "roles/compute.instanceAdmin.v1",
  "roles/billing.user",
  "roles/serviceusage.serviceUsageConsumer",
];

const setupIamResourceMap = {
  projects: "$project_id",
  "resource-manager folders": "$folder_id",
  organizations: "$organization_id",
};

const varReplaceKey = {
  eztf_config_name: "ez_config_name",
  output_git_uri: "ez_repo_git_uri",
  gcs_bucket: "setup_gcs",
  gcs_bucket_location: "setup_gcs_location",
};

function fixVariable(data, rangeName) {
  if (!data) return data;
  for (const [key, val] of Object.entries(varReplaceKey)) {
    if (data.hasOwnProperty(key)) {
      data[val] = data[key];
      delete data[key];
    }
  }
  if (rangeName === "variable") {
    if (!data.setup_roles) {
      data.setup_roles = defaultSetupRoles;
    }
    if (!data.setup_apis) {
      data.setup_apis = defaultSetupApis;
    }
    if (!data.setup_iam_resource) {
      data.setup_iam_resource = "organizations";
    }
  }
  if (!data.setup_iam_resource) {
    data.setup_iam_resource = "projects";
  }
  if (!data.setup_iam_resource_id) {
    data.setup_iam_resource_id =
      setupIamResourceMap[data.setup_iam_resource] || "";
  }
  return data;
}

function fixJsonYamlMap(data) {
  if (!data) return data;
  let dicKey = data._map_key;
  if (dicKey) {
    let newData = {};
    delete data._map_key;
    newData[dicKey] = data;
    return newData;
  }
  return data;
}

function fixGroup(data) {
  if (!data) return data;
  let idSplit = data.id.split("@");
  data.display_name = idSplit[0];
  data.types = ["default"];
  data.domain = idSplit[1];
  return data;
}

function iamPrincipal(name, type) {
  name = rmBracket(name);

  if (type.startsWith("principal") && name.split("/").length === 3) {
    let prefixWorkforce =
      "//iam.googleapis.com/locations/global/workforcePools";
    name = `${prefixWorkforce}/${name}`;
  }
  return `${type}:${name}`;
}

function fixIam(data) {
  if (!data) return data;
  data.principal = iamPrincipal(data.principal, data.principal_type);
  return data;
}

function fixProject(data) {
  let hostOrService = lower(data.enable_shared_vpc_host_project);
  if (hostOrService === "host_project") {
    data.enable_shared_vpc_host_project = true;
    delete data.svpc_host_project_id;
    delete data.shared_vpc_subnets;
  } else if (hostOrService === "service_project") {
    delete data.enable_shared_vpc_host_project;
  }
  if (data.group_name) {
    data.domain = data.group_name.split("@")[1];
    data.group_name = data.group_name.split("@")[0];
    data.group_role = "roles/viewer";
  }
  return data;
}

function fixFirewall(data) {
  let protocol_ports = [];
  for (const val of sepArray(data.protocol_ports, ";")) {
    const [protocol, ports] = val.split(":");
    protocol_ports.push({ protocol: protocol, ports: sepArray(ports) });
  }
  data[data.action] = protocol_ports;
  data[`source_${data.source_filter_type}`] = data.source_filter_value;
  data[`destination_${data.destination_filter_type}`] =
    data.destination_filter_value;
  delete data.protocol_ports;
  delete data.source_filter_type;
  delete data.source_filter_value;
  delete data.destination_filter_type;
  delete data.destination_filter_value;
  delete data.action;
  return data;
}

const mapLogDest = {
  pubsub: "topic_name",
  storage: "storage_bucket_name",
  logbucket: "name",
  bigquery: "dataset_name",
};

function fixLogging(data) {
  data.logsink.log_sink_name = `logsink-${data.name}`;
  let destination = data.log_destination_type;
  if (!data[destination]) {
    data[destination] = {};
  }
  data[destination]["project_id"] = data.project_id;

  if (destination === "project") return;
  if (destination === "pubsub") delete data.location;

  data[destination][mapLogDest[destination]] = `${destination}-${data.name}`;
  if (data.location) {
    data[destination]["location"] = data.location;
  }
  delete data.name;
  delete data.location;
  delete data.project_id;
  delete data.log_destination_type;
  return data;
}

function fixVpnHa(data) {
  if (data.router_advertise_config) {
    if (data.router_advertise_config.ip_ranges) {
      data.router_advertise_config.ip_ranges = Object.fromEntries(
        data.router_advertise_config.ip_ranges.map((x) => [x, ""])
      );
    }
    data.router_advertise_config.mode =
      data.router_advertise_config.mode || "CUSTOM";
    data.router_advertise_config.groups = data.router_advertise_config
      .groups || ["ALL_SUBNETS"];
  }
  if (data.peer_external_gateway) {
    data.peer_external_gateway.interfaces =
      data.peer_external_gateway.interfaces || [];
  }
  return data;
}

function fixTunnel(data) {
  data.tunnel_name =
    data.tunnel_name ||
    `remote-${data.vpn_gateway_interface}-${data.peer_external_gateway_interface}`;
  return data;
}

function fixAgentspaceConnector(data) {
  let entities = {};
  for (const item of data.entities) {
    let filterKeyLi = item.split(".");
    let entity = filterKeyLi.pop();
    entities[item] = { entityName: entity };
    if (filterKeyLi.length >= 1) {
      let rootEntity = filterKeyLi[0];
      entities[rootEntity] = entities[rootEntity] || { entityName: rootEntity };
    }
  }

  let bodyVars = {};

  for (const filter_type of ["inclusion_filters", "exclusion_filters"]) {
    for (const key in data[filter_type]) {
      let filterVal = sepArray(data[filter_type][key]);
      // if (filterVal.length === 0) continue;
      let filterKeyLi = key.split(".");
      let filterKey = filterKeyLi.pop();
      let entityKey = filterKeyLi.join(".");
      let filterKeyVarName = pascalCase(
        filter_type.slice(0, 2) + " " + filterKey
      );
      bodyVars[filterKeyVarName] =
        "[" + filterVal.map((item) => `"${item}"`).join(", ") + "]";

      if (entities[entityKey]) {
        entities[entityKey]["params"] = entities[entityKey]["params"] || {};
        entities[entityKey]["params"][filter_type] =
          entities[entityKey]["params"][filter_type] || {};
        entities[entityKey]["params"][filter_type][
          filterKey
        ] = `$[${filterKeyVarName}]`;
      }
    }
  }

  for (const key in data["entity_params"]) {
    let entParamVal = data["entity_params"][key];
    let entParamKeyLi = key.split(".");
    let entParamKey = entParamKeyLi.pop();
    let entityKey = entParamKeyLi.join(".");
    if (entities[entityKey]) {
      entities[entityKey]["params"] = entities[entityKey]["params"] || {};
      entities[entityKey]["params"][entParamKey] = entParamVal;
    }
  }

  if (data.method === "POST") {
    data.json.dataConnector = data.json.dataConnector || {};
    var connectorBody = data.json.dataConnector;
  } else {
    data.json = data.json || {};
    var connectorBody = data.json || {};
  }
  
  let connectorSource = connectorBody.dataSource;

  for (const param in data["auth_params"]) {
    let entParamVal = data["auth_params"][param] || "";
    let authKeyName = pascalCase(connectorSource.split("_")[0] + "_" + param);
    bodyVars[authKeyName] = entParamVal;
    data["auth_params"][param] = `$\{${authKeyName}\}`;
  }
  connectorBody.params = connectorBody.params || {};
  connectorBody.entities = Object.values(entities);
  let connectorParams = connectorBody.params;

  for (const paramType of ["auth_params", "connector_params"]) {
    connectorParams = { ...connectorParams, ...data[paramType] };
  }
  for (const k in connectorParams) {
    let v = connectorParams[k];
    if (v === undefined || v === null || v === "") {
      delete connectorParams[k];
    }
  }
  connectorBody.params = connectorParams;
  data.vars = { ...data.vars, ...bodyVars };

  // console.log(JSON.stringify(data, null, 2))

  if (data.data === undefined || data.json !== undefined) {
    data.data = rpShellVar(JSON.stringify(data.json, null, 2));
  }

  //  del
  for (const key of [
    "auth_params",
    "connector_params",
    "entities",
    "exclusion_filters",
    "inclusion_filters",
    "entity_params",
    "json",
  ]) {
    delete data[key];
  }

  return data;
}

// PATCH
// update_mask=entities.params
// refreshInterval
// params
// autoRunDisabled
// actionConfig
// actionConfig.action_params
// actionConfig.service_name
// destinationConfigs
// blockingReasons
// syncMode
// incrementalSyncDisabled
// incrementalRefreshInterval
// https://cloud.google.com/generative-ai-app-builder/docs/reference/rest/v1alpha/projects.locations.collections/updateDataConnector#query-parameters

// for (const ent in entities) {
//   if (ent.startsWith(`${entityKey}.`) || entities[entityKey]) {}
// }
