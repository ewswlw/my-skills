(function(){
  var el = Array.from(document.querySelectorAll('a[data-id]')).find(function(a){
    return a.getAttribute('data-id') === 'cat_RNK_68166_-2';
  });
  if(!el) return 'cat not found';
  el.click();
  return 'clicked: ' + el.textContent.trim();
})()
