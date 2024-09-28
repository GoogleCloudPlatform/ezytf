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
