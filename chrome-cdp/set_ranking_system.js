(function(){
  function setVal(id, val) {
    var el = document.getElementById(id);
    if(!el) return 'missing: ' + id;
    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(el, val);
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
    return el.value;
  }
  
  setVal('selectedItemUid', '541832');
  setVal('selectedItemName', 'agent_lgbm_v3_ranking');
  setVal('masterrankUid', '541832');
  
  // Also update the display
  var rankDisplay = document.getElementById('rankingSystemName') || 
                    document.querySelector('[id*=rankSys],[id*=rankingSystem]');
  
  // Click the item in the tree via JS to trigger P123's selection logic
  var treeItem = Array.from(document.querySelectorAll('a[data-id]')).find(function(a){
    return a.getAttribute('data-id') === 'item_RNK_68166_-6_541832';
  });
  
  if(treeItem) {
    treeItem.click();
    return 'clicked tree item: ' + treeItem.textContent.trim() + 
           ' | uid=' + document.getElementById('selectedItemUid').value;
  }
  
  return 'tree item not clickable, set uid=' + document.getElementById('selectedItemUid').value + 
         ', name=' + document.getElementById('selectedItemName').value;
})()
