import { mergeObjArray, lower, groupAddon } from "../util.js";
import { readNamedRange, readMapRange } from "../format.js";

export {
  modifyVpnHa,
  modifyIam,
  modifyFoldersProject,
  modifyNetworkFirewall,
  modifyFwPolicyRh,
  modifyFwPolicyNw,
};

function modifyVpnHa(eztf, resourceRangeMap) {
  const vpnHaRange = resourceRangeMap["vpn_ha"] || "";
  const vpnHaTunnelRange = resourceRangeMap["vpn_ha_tunnel"] || "";
  const externalVpnGatewayRange = `external_vpn_gateway_${vpnHaRange}`;
  let vpnHaArray = readMapRange(eztf, vpnHaRange);
  let tunnelArray = readMapRange(eztf, vpnHaTunnelRange);
  let [vpnHa, externalGateways] = groupVpnHa(vpnHaArray, tunnelArray);
  if (externalGateways.length > 0) {
    eztf.eztfConfig[externalVpnGatewayRange] = externalGateways;
  }
  eztf.eztfConfig[vpnHaRange] = vpnHa;
}

function groupVpnHa(vpnHaArray, tunnelArray) {
  let vpnHaObj = {};
  let extGateways = [];
  vpnHaArray.forEach((vpn) => {
    vpnHaObj[vpn["name"]] = vpn;
  });

  let tunnelsObj = tunnelArray.reduce((tunnel, t) => {
    if (!tunnel[t.name]) {
      tunnel[t.name] = {};
    }
    tunnel[t.name][t.tunnel_name] = t;

    if (t.peer_external_gateway_self_link) {
      extGateways.push({
        name: t.peer_external_gateway_self_link,
        project: vpnHaObj[t.name]["project_id"],
        redundancy_type: "SINGLE_IP_INTERNALLY_REDUNDANT",
        interface: [
          {
            id: 0,
            ip_address: t.ip_address,
          },
        ],
      });
    } else if (t.ip_address) {
      vpnHaObj[t.name]["peer_external_gateway"]["interfaces"].push({
        id: t.peer_external_gateway_interface,
        ip_address: t.ip_address,
      });
    }
    delete t.ip_address;
    delete t.name;
    delete t.tunnel_name;
    return tunnel;
  }, {});

  for (const [name, vpn] of Object.entries(vpnHaObj)) {
    if (tunnelsObj[name]) {
      vpn["tunnels"] = tunnelsObj[name];
    }
    if (vpn.peer_external_gateway) {
      if (vpn.peer_external_gateway.interfaces) {
        vpn["peer_external_gateway"]["interfaces"].sort((a, b) => {
          return a.id - b.id;
        });
      }
    }
  }
  let vpnHa = Object.values(vpnHaObj);
  return [vpnHa, extGateways];
}

function modifyIam(eztf, resourceRangeMap) {
  const iamRangeName = resourceRangeMap["iam"] || "";
  eztf.eztfConfig[iamRangeName] = groupIam(readMapRange(eztf, iamRangeName));
}

function modifyFoldersProject(eztf, resourceRangeMap) {
  const foldersRange = resourceRangeMap["folders"] || "";
  const projectRange = resourceRangeMap["projects"] || "";
  let [headers, fldrValue] = readNamedRange(eztf, foldersRange);
  let [folders, folderSet, projectsFolder] = groupFolders(headers, fldrValue);
  if (foldersRange) {
    eztf.eztfConfig[foldersRange] = folders;
  }
  if (projectRange) {
    let projectData = readMapRange(eztf, projectRange);
    let mergeProject = mergeObjArray(
      projectData,
      Object.values(projectsFolder),
      "name"
    );
    eztf.eztfConfig[projectRange] = Object.values(mergeProject);
  }
}

function modifyNetworkFirewall(eztf, resourceRangeMap) {
  const networkRange = resourceRangeMap["network"] || "";
  const firewallRange = resourceRangeMap["firewall"] || "";
  const routerRange = `router_${networkRange}`;
  let networkArrayObj = readMapRange(eztf, networkRange);
  let [networkObj, network, nats] = groupNetwork(networkArrayObj);
  if (firewallRange) {
    let firewallArrayObj = readMapRange(eztf, firewallRange);
    eztf.eztfConfig[firewallRange] = groupFirewall(firewallArrayObj, networkObj);
  }
  if (networkRange) {
    eztf.eztfConfig[networkRange] = network;
    eztf.eztfConfig[routerRange] = nats;
  }
}

function groupFirewall(fwArray, network) {
  let firewallObj = fwArray.reduce((firewall, rule) => {
    let nw = rule.network_name;
    let direction = `${rule.direction}_rules`;
    if (!firewall[nw]) {
      firewall[nw] = { network_name: nw };
    }
    if (network[nw]) {
      firewall[nw]["project_id"] = network[nw]["project_id"];
    }
    if (!firewall[nw][direction]) firewall[nw][direction] = [];
    firewall[nw][direction].push(rule);
    delete rule.network_name;
    delete rule.direction;
    return firewall;
  }, {});
  return Object.values(firewallObj);
}

function groupIam(access) {
  return access.reduce((iam, row) => {
    if (!iam[row.node]) {
      iam[row.node] = {};
    }
    iam[row.node][row.principal] = row.roles;
    return iam;
  }, {});
}

function groupFolders(fldr_header, fldr) {
  let folders = {};
  let folderSet = new Set();
  let projectsFolder = {};
  let levels = fldr_header.indexOf("project");

  for (let i = 0; i < fldr.length; i++) {
    const row = fldr[i];
    let currentLevel = folders;
    for (let j = 0; j < levels; j++) {
      if (
        i > 0 &&
        !row[j] &&
        ((j > 0 && row[j - 1] === fldr[i - 1][j - 1]) || j === 0)
      ) {
        row[j] = fldr[i - 1][j];
      }
      let key = row[j];
      if (key) {
        currentLevel[key] = currentLevel[key] || {};
        if (!Object.prototype.hasOwnProperty.call(currentLevel, key)) {
          currentLevel[key] = {};
        }
        currentLevel = currentLevel[key];
      }
    }
    let project = row[levels];
    let rowFolders = row.slice(0, levels).filter(Boolean);
    let folderId = "/" + rowFolders.join("/");
    let folderPaths = rowFolders.map(
      (s, i) => "/" + rowFolders.slice(0, i + 1).join("/")
    );
    folderPaths.forEach((item) => folderSet.add(item));
    if (project) {
      projectsFolder[project] = { name: project };
      if (folderId != "/") {
        projectsFolder[project]["folder_id"] = folderId;
      }
    }
  }
  return [folders, folderSet, projectsFolder];
}

function groupNats(networks) {
  let cr = [];
  for (const nw of networks) {
    let obj = {
      network: nw.network_name,
      project: nw.project_id,
    };
    for (let [region, subnets] of Object.entries(nw.nats)) {
      if ("region" in subnets) {
        subnets = ["region"];
      }
      let crObj = { ...obj, region: region };
      let natObj = {
        log_config: {
          enable: true,
          filter: "ERRORS_ONLY",
        },
      };
      natObj.source_subnetwork_ip_ranges_to_nat =
        "ALL_SUBNETWORKS_ALL_IP_RANGES";
      if (subnets[0] != "region") {
        natObj.source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS";
        let subnetworks = subnets.map((subnet) => {
          return {
            name: `${region}/${subnet}`,
            source_ip_ranges_to_nat: ["ALL_IP_RANGES"],
          };
        });
        natObj.subnetworks = subnetworks;
      }
      crObj = { ...obj, region: region, nats: [natObj] };
      cr.push(crObj);
    }
  }
  return cr;
}

function groupNetwork(networkArray) {
  let networksObj = networkArray.reduce((network, nw) => {
    let sub = fixSubnet(nw.subnet);
    let nwName = nw.network_name;
    let subnet = sub["subnet_name"];
    let region = sub["subnet_region"];

    delete nw["subnet"];

    if (!network[nwName]) {
      network[nwName] = { ...nw, subnets: [], nats: {} };
    }
    if (subnet) {
      network[nwName]["subnets"].push(sub);
    }
    if (nw.secondary_ranges) {
      network[nwName]["secondary_ranges"] = {
        ...network[nwName]["secondary_ranges"],
        ...nw.secondary_ranges,
      };
    }
    if (region && nw.nat && lower(nw.nat) !== "off") {
      let subNat = lower(nw.nat) === "region" ? "region" : subnet;
      if (!network[nwName]["nats"][region]) {
        network[nwName]["nats"][region] = [];
      }
      network[nwName]["nats"][region].push(subNat);
    }
    return network;
  }, {});
  let networks = Object.values(networksObj);
  let router = groupNats(networks);
  networks.forEach((nw) => ["nats", "nat"].forEach((k) => delete nw[k]));
  return [networksObj, networks, router];
}

function fixSubnet(data) {
  if (!data.subnet_name || !data.subnet_ip || !data.subnet_region) {
    return {};
  }
  if (lower(data.subnet_private_access) === "on")
    data.subnet_private_access = true;
  if (lower(data.subnet_flow_logs) === "on") {
    data.subnet_flow_logs = true;
    data.subnet_flow_logs_sampling = data.subnet_flow_logs_sampling || "0.5";
    data.subnet_flow_logs_metadata =
      data.subnet_flow_logs_metadata || "INCLUDE_ALL_METADATA";
    data.subnet_flow_logs_interval =
      data.subnet_flow_logs_interval || "INTERVAL_10_MIN";
  } else {
    delete data.subnet_flow_logs;
  }
  return data;
}

function modifyFwPolicyRh(eztf, resourceRangeMap) {
  const fprhRangeName = resourceRangeMap["firewall_policy_rh"] || "";
  eztf.eztfConfig[fprhRangeName] = Object.values(
    groupAddon(readMapRange(eztf, fprhRangeName), "policy_name", "rules")
  );
}

function modifyFwPolicyNw(eztf, resourceRangeMap) {
  const fpnwRangeName = resourceRangeMap["firewall_policy_nw"] || "";
  eztf.eztfConfig[fpnwRangeName] = Object.values(
    groupAddon(readMapRange(eztf, fpnwRangeName), "policy_name", "rules")
  );
}
