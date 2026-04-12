(function(){
  var ta = Array.from(document.querySelectorAll('textarea')).find(function(t){
    return t.getBoundingClientRect().width > 0;
  });
  if(!ta) return 'textarea not found';
  
  var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  setter.call(ta, '[Rank] RankPos > 35\n[Sell2] \n[Sell3] ');
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  ta.dispatchEvent(new Event('change', {bubbles: true}));
  
  return 'set: ' + ta.value;
})()
