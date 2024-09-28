import { mergeAddon } from "../util.js";
import { readMapRange } from "../format.js";

export { modifyPgsql, modifyMysql, fixCloudSql };

function modifyPgsql(eztf, resourceRangeMap) {
  const pgsqlRange = resourceRangeMap["pgsql"] || "";
  const pgsqlReplicaRange = resourceRangeMap["pgsql_replica"] || "";
  let pgsqlArray = readMapRange(eztf, pgsqlRange);
  let pgsqlReplicaArray = readMapRange(eztf, pgsqlReplicaRange);
  let pgsql = mergeAddon(
    pgsqlArray,
    pgsqlReplicaArray,
    "name",
    "master_name",
    "read_replicas"
  );
  eztf.eztfConfig[pgsqlRange] = pgsql;
}

function modifyMysql(eztf, resourceRangeMap) {
  const mysqlRange = resourceRangeMap["mysql"] || "";
  const mysqlReplicaRange = resourceRangeMap["mysql_replica"] || "";
  let mysqlArray = readMapRange(eztf, mysqlRange);
  let mysqlReplicaArray = readMapRange(eztf, mysqlReplicaRange);
  let mysql = mergeAddon(
    mysqlArray,
    mysqlReplicaArray,
    "name",
    "master_name",
    "read_replicas"
  );
  eztf.eztfConfig[mysqlRange] = mysql;
}

function fixCloudSql(sql) {
  let newDatabaseFlags = [];
  for (const [key, value] of Object.entries(sql.database_flags)) {
    newDatabaseFlags.push({
      name: key,
      value: value,
    });
  }
  sql.database_flags = newDatabaseFlags;
  const authorizedIpRange = sql?.ip_configuration?.authorized_networks;
  if (authorizedIpRange) {
    sql.ip_configuration.authorized_networks = authorizedIpRange.map(
      (ipRange) => {
        return { name: `${sql.name}-${ipRange}-cidr`, value: ipRange };
      }
    );
  }
  return sql;
}
