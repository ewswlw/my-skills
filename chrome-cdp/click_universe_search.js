(function(){
  // Click the Universe button first
  var btn = Array.from(document.querySelectorAll('button')).find(function(b){
    return b.textContent.trim().includes('Easy to Trade US');
  });
  if(btn) {
    btn.click();
    return 'clicked universe button';
  }
  return 'button not found';
})()
