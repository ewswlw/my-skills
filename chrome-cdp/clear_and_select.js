const expr = `(function() {
  // Find "Clear selection" button and click it
  var clearBtn = Array.from(document.querySelectorAll('button, a')).find(e => e.textContent.trim() === 'Clear selection');
  if (clearBtn) { clearBtn.click(); }
  
  // Wait then check state
  return 'cleared: ' + (clearBtn ? 'yes' : 'no');
})()`;
process.stdout.write(expr);
