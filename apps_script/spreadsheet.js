var logSheet = 'Changelog'; // name of the Sheet where data needs to be logged
var backlogSheet = 'Backlog'; // name of the Sheet where data is entered

var columnStart = 1;
var columnEnd = 52;
var uuidColumn = "AX";
var createdAtColumn = "AY";
var lastUpdatedAtColumn = "AZ";

function getUuid() {
  return Utilities.getUuid();
}

function getNow() {
  var dateobj = new Date
  var date = dateobj.toISOString();
  return date;
}


function onEdit(e) {
  var now = new Date();
  var oldVal = e.oldValue; // "Only available if the edited range is a single cell. Will be undefined if the cell had no previous content."
  var newVal = e.value;
  var sheetName = e.source.getSheetName();
  var activeCell = e.range.getA1Notation();

  var editedRow = activeCell.slice(-1)
  var editedColumn = activeCell.slice(0,activeCell.length -1)


  // Check if it's a row being added
  if (e.range.columnStart == 1 && e.range.columnEnd == columnEnd) {
    newRowAutoPopulate(editedRow);
  }
  else {
    Logger.log("UPDATING");
  }


  if (sheetName !== logSheet && editedRow !== "1") {

    if (oldVal === 'Copy this row to add an initiative' || oldVal === 'example_row' || oldVal === undefined) {
      oldVal = '';
    }
    updateLastUpdated(editedRow);

    var labelCell = editedColumn + 1;
    var projectId = getValue(uuidColumn + editedRow);

    SpreadsheetApp
    .getActiveSpreadsheet()
    .getSheetByName(logSheet)
    .appendRow(
      [
        getNow(),
        projectId,
        getValue(labelCell),
        oldVal,
        newVal,
        sheetName
      ]
    );
  }
}


function getValue(activeCellA1Notation) {
  return SpreadsheetApp.getActiveSheet().getRange(activeCellA1Notation).getValue();
}

function addUuid(thisRow) {
  updateField(uuidColumn, thisRow, getUuid())
}


function addCreatedAt(thisRow) {
  updateField(createdAtColumn, thisRow, getNow())
}


function updateLastUpdated(thisRow) {
  updateField(lastUpdatedAtColumn, thisRow, getNow())
}


function newRowAutoPopulate(thisRow) {
    addUuid(thisRow);
    addCreatedAt(thisRow);
    updateLastUpdated(thisRow);
}


function updateField(fieldColumn, fieldRow, value) {
  Logger.log(fieldColumn + fieldRow);
  Logger.log(value);
    SpreadsheetApp
    .getActiveSpreadsheet()
    .getSheetByName(backlogSheet)
    .getRange(fieldColumn + fieldRow)
    .setValue(value);
}
