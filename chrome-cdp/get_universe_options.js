(function(){
  var sel = document.getElementById('universeUid') || 
            document.querySelector('select[name*=universe]') ||
            document.querySelector('select');
  if(!sel) return 'no select found';
  return JSON.stringify({
    id: sel.id,
    value: sel.value,
    currentText: sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].text : 'none',
    totalOptions: sel.options.length,
    sample: Array.from(sel.options).filter(function(o){
      return o.text.toLowerCase().includes('otc') || 
             o.text.toLowerCase().includes('no finance') ||
             o.text.toLowerCase().includes('min 10') ||
             o.text.toLowerCase().includes('easy');
    }).slice(0,10).map(function(o){return {val:o.value, text:o.text};})
  });
})()
