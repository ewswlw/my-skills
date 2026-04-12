(function(){
  var el = document.activeElement;
  var sr = el.shadowRoot;
  if(!sr) {
    // Try to find the shadow host
    var hosts = Array.from(document.querySelectorAll('*')).filter(function(e){
      return e.shadowRoot !== null;
    });
    if(hosts.length === 0) return 'no shadow hosts found';
    el = hosts[hosts.length - 1]; // take last one (most likely the dialog)
    sr = el.shadowRoot;
  }
  
  var nameInput = sr.querySelector('input[type=text]');
  if(!nameInput) return 'name input not found in shadow root';
  
  // Set new name value
  var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  setter.call(nameInput, 'agent_lgbm_v3_strategy');
  nameInput.dispatchEvent(new Event('input', {bubbles: true}));
  nameInput.dispatchEvent(new Event('change', {bubbles: true}));
  
  // Now find and click the Save button
  var buttons = Array.from(sr.querySelectorAll('button'));
  var saveBtn = buttons.find(function(b){ return b.textContent.trim() === 'Save'; });
  
  return {
    nameSet: nameInput.value,
    saveButton: saveBtn ? 'found: ' + saveBtn.textContent.trim() : 'not found',
    allButtons: buttons.map(function(b){ return b.textContent.trim(); })
  };
})()
