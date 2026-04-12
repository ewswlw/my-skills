(function(){
  // Update display element
  var display = document.getElementById('curRankName');
  if(display) display.textContent = 'agent_lgbm_v3_ranking';
  
  // Remove curr class from old item
  var oldCurr = document.querySelector('a.curr[data-id]');
  if(oldCurr) oldCurr.classList.remove('curr');
  
  // Add curr class to new item
  var newItem = Array.from(document.querySelectorAll('a[data-id]')).find(function(a){
    return a.getAttribute('data-id') === 'item_RNK_68166_-6_541832';
  });
  if(newItem) newItem.classList.add('curr');
  
  // Also update the right panel
  var rightTitle = document.querySelector('.select-right-cont a');
  if(rightTitle) rightTitle.textContent = 'agent_lgbm_v3_ranking';
  
  return {
    displayUpdated: display ? display.textContent : 'not found',
    selectedUid: document.getElementById('selectedItemUid').value,
    masterUid: document.getElementById('masterrankUid').value
  };
})()
