const expr = `(function() {
  var allText = Array.from(document.querySelectorAll('*')).filter(e => e.textContent.trim() === 'lightgbm slow 2' && e.children.length === 0);
  for (var t of allText) {
    var row = t.closest('tr') || t.closest('li') || t.parentElement?.parentElement;
    if (row) {
      var cb = row.querySelector('input[type=checkbox]');
      if (cb) { cb.click(); return 'clicked: ' + cb.checked; }
    }
  }
  var cbs = document.querySelectorAll('input[type=checkbox]');
  if (cbs[1]) { cbs[1].click(); return 'clicked 2nd checkbox: ' + cbs[1].checked; }
  return 'not found';
})()`;
process.stdout.write(expr);
