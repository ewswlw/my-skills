(function(){
  var ta = Array.from(document.querySelectorAll('textarea')).find(function(t){
    return t.getBoundingClientRect().top > 200;
  });
  if(!ta) return 'not found';
  var newVal = '[Rank] RankPos > 25\n[Sell1] \n[Sell2] ';
  var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  setter.call(ta, newVal);
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  ta.dispatchEvent(new Event('change', {bubbles: true}));
  return 'set: ' + ta.value;
})()
