(function(){
  var results = {};
  
  // 1. Change universe to training universe (ID 320031)
  var uniInput = document.getElementById('universeUid');
  if(uniInput) {
    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(uniInput, '320031');
    uniInput.dispatchEvent(new Event('change', {bubbles: true}));
    results.universe = 'set to 320031 (was ' + '73975)';
  } else {
    results.universe = 'universeUid input not found';
  }
  
  // Update universe display name if present
  var uniDisplay = document.getElementById('universeName') || 
                   document.querySelector('[id*=universe][id*=name]');
  if(uniDisplay) {
    uniDisplay.textContent = 'No OTC Exchange + min 10 mil No Finance2';
    results.universeDisplay = 'updated';
  }
  
  return JSON.stringify(results);
})()
