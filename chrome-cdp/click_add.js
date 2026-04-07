const expr = `(function() {
  var btns = Array.from(document.querySelectorAll('button')).filter(e => e.getBoundingClientRect().width > 0);
  var addBtn = btns.find(e => /^Add/.test(e.textContent.trim()));
  if (addBtn) { addBtn.click(); return 'clicked: ' + addBtn.textContent.trim(); }
  return 'not found: ' + btns.map(e => e.textContent.trim()).join(',');
})()`;
process.stdout.write(expr);
