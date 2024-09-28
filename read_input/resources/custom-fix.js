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

import { lower, rmBracket, sepArray } from "../util.js";

export {
  fixGroup,
  fixLogging,
  fixProject,
  fixFirewall,
  fixIam,
  fixVpnHa,
  fixTunnel,
};

function fixGroup(data) {
  if (!data) return data;
  let idSplit = data.id.split("@");
  data.display_name = idSplit[0];
  data.types = ["default"];
  data.domain = idSplit[1];
  return data;
}

function iamPrincipal(name, type, workforce_pool_id) {
  name = rmBracket(name);
  if (type.startsWith("principal")) {
    let prefixWorkforce =
      "//iam.googleapis.com/locations/global/workforcePools";
    switch (name.split("/").length) {
      case 1: {
        let workforce_type = type === "principal" ? "subject" : "group";
        name = `${workforce_pool_id}/${workforce_type}/${name}`;
        break;
      }
      case 2:
        name = `${workforce_pool_id}/${name}`;
        break;
    }
    name = `${prefixWorkforce}/${name}`;
  }
  return `${type}:${name}`;
}

function fixIam(data, eztf) {
  if (!data) return data;
  let workforce_pool_id =
    eztf.eztfConfig["variable"]["workforce_pool_id"] || "";
  data.principal = iamPrincipal(
    data.principal,
    data.principal_type,
    workforce_pool_id
  );
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
