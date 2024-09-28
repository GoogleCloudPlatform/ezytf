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
