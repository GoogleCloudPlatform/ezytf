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

import * as fd from "./foundation.js";
import * as gke from "./gke.js";
import * as sc from "./vpc-sc.js";
import * as cus from "./custom-fix.js";
import * as db from "./database.js";
import { mapTfRanges } from "../format.js";
export { mapEntry, modifyResource };

const mapEntry = {
  tfgenerate: mapTfRanges,
  groups: cus.fixGroup,
  iam: cus.fixIam,
  projects: cus.fixProject,
  firewall: cus.fixFirewall,
  logging: cus.fixLogging,
  vpn_ha: cus.fixVpnHa,
  vpn_ha_tunnel: cus.fixTunnel,
  sc_ingress_egress: sc.fixScPolicies,
  pgsql: db.fixCloudSql,
  pgsql_replica: db.fixCloudSql,
  mysql: db.fixCloudSql,
  mysql_replica: db.fixCloudSql,
  mssql: db.fixCloudSql,
};

const modifyResource = {
  iam: fd.modifyIam,
  folders: fd.modifyFoldersProject,
  projects: fd.modifyFoldersProject,
  network: fd.modifyNetworkFirewall,
  firewall: fd.modifyNetworkFirewall,
  firewall_policy_rh: fd.modifyFwPolicyRh,
  firewall_policy_nw: fd.modifyFwPolicyNw,
  vpn_ha: fd.modifyVpnHa,
  vpn_ha_tunnel: fd.modifyVpnHa,
  gke: gke.modifyGke,
  gke_private: gke.modifyPrivateGke,
  sc_perimeter: sc.modifyPerimeter,
  sc_ingress_egress: sc.modifyPerimeter,
  pgsql: db.modifyPgsql,
  pgsql_replica: db.modifyPgsql,
  mysql: db.modifyMysql,
  mysql_replica: db.modifyMysql,
};
