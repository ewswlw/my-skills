(function(){
  // Find elements showing "Core Combination" and update them
  var allText = Array.from(document.querySelectorAll('*')).filter(function(el){
    return el.childNodes.length === 1 && 
           el.childNodes[0].nodeType === 3 && 
           el.textContent.trim() === 'Core Combination' &&
           el.getBoundingClientRect().width > 0;
  });
  
  var rankSysEl = document.querySelector('td.detail-value a, .rankSysName, #rankSysName, [id*=rankSys]');
  
  // Try to find the display for Ranking System
  var rankingLabel = Array.from(document.querySelectorAll('a,span,div')).filter(function(el){
    return el.textContent.trim() === 'Core Combination' && el.getBoundingClientRect().width > 0;
  });
  
  return JSON.stringify({
    allText: allText.length,
    rankSysEl: rankSysEl ? rankSysEl.outerHTML.substring(0,100) : null,
    rankingLabels: rankingLabel.slice(0,5).map(function(el){
      return {tag:el.tagName, id:el.id, class:el.className.substring(0,30), html:el.outerHTML.substring(0,80)};
    })
  });
})()
