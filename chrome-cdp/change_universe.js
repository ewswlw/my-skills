(function(){
  var results = {};
  
  // Change the hidden universeUid input
  var uniInput = document.getElementById('universeUid');
  if(uniInput) {
    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(uniInput, '320031');
    uniInput.dispatchEvent(new Event('input', {bubbles: true}));
    uniInput.dispatchEvent(new Event('change', {bubbles: true}));
    results.universeUid = 'set to 320031, now: ' + uniInput.value;
  }
  
  // Find and update the visible universe display 
  // It could be a span, a select, or a custom dropdown
  var allVisible = Array.from(document.querySelectorAll('*')).filter(function(e) {
    return e.getBoundingClientRect().height > 0 && 
           e.getBoundingClientRect().width > 0 &&
           (e.textContent.trim() === 'Easy to Trade US' ||
            e.value === 'Easy to Trade US');
  });
  results.visibleElements = allVisible.map(function(e) {
    return {tag: e.tagName, id: e.id, class: e.className.substring(0,30), 
            text: e.textContent.trim().substring(0,40)};
  });
  
  // Try to find and update the select element for universe
  var uniSelect = document.querySelector('select[name=universeUid],select[id*=universe]');
  if(uniSelect) {
    var opt = Array.from(uniSelect.options).find(function(o){ return o.value === '320031'; });
    if(opt) {
      uniSelect.value = '320031';
      uniSelect.dispatchEvent(new Event('change', {bubbles: true}));
      results.selectChanged = 'changed to 320031';
    } else {
      results.selectOptions = Array.from(uniSelect.options).slice(0,5).map(function(o){return {v:o.value,t:o.text};});
    }
  }
  
  return JSON.stringify(results);
})()
