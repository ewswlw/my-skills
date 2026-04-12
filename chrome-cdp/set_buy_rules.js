(function(){
  var ta = Array.from(document.querySelectorAll('textarea')).find(function(t){
    return t.getBoundingClientRect().top > 200;
  });
  if(!ta) return 'not found';
  var newVal = '[Buy1] Rank > 90\n[Buy2] \n[Buy3] ';
  var setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  setter.call(ta, newVal);
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  ta.dispatchEvent(new Event('change', {bubbles: true}));
  return 'set: ' + ta.value;
})()
