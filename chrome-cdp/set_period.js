(function(){
  var results = {};
  
  // Find and update the dateRange text input (visible)
  var dateRange = document.getElementById('dateRange');
  if(dateRange) {
    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(dateRange, '01/02/2021 - 12/27/2025');
    dateRange.dispatchEvent(new Event('input', {bubbles: true}));
    dateRange.dispatchEvent(new Event('change', {bubbles: true}));
    // Also fire blur/keyup to trigger any listeners
    dateRange.dispatchEvent(new Event('blur', {bubbles: true}));
    results.dateRange = dateRange.value;
  }
  
  // Look for hidden start/end date inputs
  var allInputs = Array.from(document.querySelectorAll('input[type=hidden]')).filter(function(i){
    return i.id && (i.id.includes('start') || i.id.includes('end') || i.id.includes('from') || i.id.includes('to') || i.id.includes('Date'));
  });
  results.hiddenInputs = allInputs.map(function(i){ return {id: i.id, val: i.value}; });
  
  // Also look for separate start/end date inputs
  var startInput = document.getElementById('startDate') || document.getElementById('dtStart') || document.getElementById('start');
  var endInput = document.getElementById('endDate') || document.getElementById('dtEnd') || document.getElementById('end');
  if(startInput) {
    var setter2 = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter2.call(startInput, '01/02/2021');
    startInput.dispatchEvent(new Event('change', {bubbles: true}));
    results.startInput = startInput.value;
  }
  
  return JSON.stringify(results);
})()
