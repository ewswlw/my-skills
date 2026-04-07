const expr = `Array.from(document.querySelectorAll('button')).find(e=>e.getBoundingClientRect().width>0&&/^Add/.test(e.textContent.trim())&&!/Add Model/.test(e.textContent.trim()))?.click(),'done'`;
process.stdout.write(expr);
