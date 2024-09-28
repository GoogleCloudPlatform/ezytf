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

function populateFoldersProjects(folderRangeName, writeRangeTitle) {
  let [fldr_header, fldr] = readNamedRange(folderRangeName)
  let folderProjectSet = new Set();
  let levels = fldr_header.indexOf("project")

  for (let i = 0; i < fldr.length; i++) {
    const row = fldr[i];
    for (let j = 0; j < levels; j++) {
      if ((i > 0 && !row[j]) &&
        ((j > 0 && row[j - 1] === fldr[i - 1][j - 1]) || j === 0)) {
        row[j] = fldr[i - 1][j];
      }
    }
    let project = row[levels]
    let rowFolders = row.slice(0, levels).filter(Boolean)
    let folderPaths = rowFolders.map((s, i) => '/' + rowFolders.slice(0, i + 1).join('/'))
    folderPaths.forEach(item => folderProjectSet.add(item))
    if (project) {
      folderProjectSet.add(project)
    }
  }
  folderProjectSet.add('/')
  let folderRows = Array.from(folderProjectSet).toSorted().map(item => [item]);
  console.log(folderRows)
  clearContentColumn(writeRangeTitle, 100)
  writeRange(folderRows, writeRangeTitle)
}