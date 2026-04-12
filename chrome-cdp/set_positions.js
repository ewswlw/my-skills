(function(){
  var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  
  // Change number of positions from 20 to 10
  var numPos = document.getElementById('rebal_num_pos');
  setter.call(numPos, '10');
  numPos.dispatchEvent(new Event('input', {bubbles: true}));
  numPos.dispatchEvent(new Event('change', {bubbles: true}));
  
  // Change position weight from 5.0% to 10.0% (100/10)
  var posWeight = document.getElementById('posWeight');
  setter.call(posWeight, '10.0');
  posWeight.dispatchEvent(new Event('input', {bubbles: true}));
  posWeight.dispatchEvent(new Event('change', {bubbles: true}));
  
  return {
    numPos: numPos.value,
    posWeight: posWeight.value
  };
})()
