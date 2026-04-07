// Select only lightgbm slow 2 checkbox in the Add Models dialog
const expr = `(function() {
  // Find all table rows in the dialog
  var rows = Array.from(document.querySelectorAll('tr, .list-row, .table-row, [role=row]'));
  
  // Find the row containing exactly "lightgbm slow 2"
  var targetRow = rows.find(row => {
    var cells = row.querySelectorAll('td, .cell, a, span');
    return Array.from(cells).some(cell => cell.textContent.trim() === 'lightgbm slow 2');
  });
  
  if (!targetRow) {
    // Try alternative: find element with text "lightgbm slow 2"
    var elements = Array.from(document.querySelectorAll('a, span, td'));
    var el = elements.find(e => e.textContent.trim() === 'lightgbm slow 2');
    if (el) {
      // Go up to find containing row
      var parent = el.parentElement;
      while (parent && !parent.matches('tr, [role=row]')) {
        parent = parent.parentElement;
      }
      targetRow = parent;
    }
  }
  
  if (!targetRow) return 'Row not found';
  
  var cb = targetRow.querySelector('input[type=checkbox]');
  if (!cb) return 'Checkbox not found in row';
  
  if (!cb.checked) {
    cb.click();
    return 'Checked: ' + cb.checked;
  } else {
    return 'Already checked';
  }
})()`;
process.stdout.write(expr);
