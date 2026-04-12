(function(){
  var hosts = Array.from(document.querySelectorAll('*')).filter(function(e){
    return e.shadowRoot !== null && e.shadowRoot.querySelector('button');
  });
  if(hosts.length === 0) return 'no shadow hosts with buttons';
  
  var lastHost = hosts[hosts.length - 1];
  var sr = lastHost.shadowRoot;
  var saveBtn = Array.from(sr.querySelectorAll('button')).find(function(b){
    return b.textContent.trim() === 'Save';
  });
  
  if(!saveBtn) return 'Save button not found';
  saveBtn.click();
  return 'clicked Save: ' + saveBtn.textContent.trim();
})()
