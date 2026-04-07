const expr = `Array.from(document.querySelectorAll('a,span,td')).find(e=>e.textContent.trim()==='lightgbm slow 2')?.closest('tr,[role=row]')?.querySelector('input[type=checkbox]')?.click(),'done'`;
process.stdout.write(expr);
