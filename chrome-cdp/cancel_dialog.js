const expr = `(function() {
  var btns = Array.from(document.querySelectorAll('button')).filter(e => e.getBoundingClientRect().width > 0);
  var cancelBtn = btns.find(e => e.textContent.trim() === 'Cancel');
  if (cancelBtn) { cancelBtn.click(); return 'cancelled: ' + JSON.stringify(cancelBtn.getBoundingClientRect()); }
  return 'Cancel not found. Visible buttons: ' + btns.map(e => e.textContent.trim().substring(0,20) + '@' + Math.round(e.getBoundingClientRect().top)).join(', ');
})()`;
process.stdout.write(expr);
