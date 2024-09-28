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