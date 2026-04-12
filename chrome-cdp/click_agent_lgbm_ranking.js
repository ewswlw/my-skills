(function(){
  var el = Array.from(document.querySelectorAll('a[data-id]')).find(function(a){
    return a.getAttribute('data-id') === 'item_RNK_68166_-6_541832';
  });
  if(!el) {
    // Try expanding Unclassified first
    var unc = Array.from(document.querySelectorAll('a[data-id]')).find(function(a){
      return a.getAttribute('data-id') === 'cat_RNK_68166_-6';
    });
    if(unc) { unc.click(); return 'clicked unclassified: ' + unc.textContent.trim(); }
    return 'item not found';
  }
  el.click();
  return 'clicked: ' + el.textContent.trim();
})()
