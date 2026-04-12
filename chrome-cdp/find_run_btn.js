// Try shadow DOM traversal and various methods to find the Run button
function findInShadow(root) {
  var els = Array.from(root.querySelectorAll('*'));
  for (var el of els) {
    if (el.shadowRoot) {
      var found = findInShadow(el.shadowRoot);
      if (found) return found;
    }
    if ((el.tagName === 'BUTTON' || el.getAttribute('role') === 'button') && el.textContent.trim() === 'Run') {
      return el;
    }
  }
  return null;
}
var btn = findInShadow(document);
if (btn) {
  var r = btn.getBoundingClientRect();
  JSON.stringify({found: true, tag: btn.tagName, rect: r.toJSON(), outerHTML: btn.outerHTML.substring(0, 200)});
} else {
  // Last resort - look for any element with just "Run" in a small area
  var candidates = Array.from(document.querySelectorAll('*')).filter(e => {
    var t = e.textContent.trim();
    var r = e.getBoundingClientRect();
    return t === 'Run' && r.width > 0 && r.height > 0;
  });
  JSON.stringify({found: false, candidates: candidates.map(e => ({tag: e.tagName, text: e.textContent.trim(), rect: e.getBoundingClientRect().toJSON()}))});
}
