(function(){
  // Find the search input in the universe picker modal
  var searchInputs = Array.from(document.querySelectorAll('input[type=search],input[type=text],input[placeholder*=earch]'))
    .filter(function(i){ return i.getBoundingClientRect().width > 0; });
  
  if(searchInputs.length === 0) return 'no search input found';
  
  // Find the one inside the modal (has the smallest y position = near top of modal)
  var modalSearch = searchInputs.reduce(function(a, b) {
    return a.getBoundingClientRect().top < b.getBoundingClientRect().top ? a : b;
  });
  
  // Set the value to search for training universe
  var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  setter.call(modalSearch, 'No OTC');
  modalSearch.dispatchEvent(new Event('input', {bubbles: true}));
  modalSearch.dispatchEvent(new Event('change', {bubbles: true}));
  
  // Also try keyboard event
  modalSearch.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true, key: 'c'}));
  
  return {
    found: true,
    placeholder: modalSearch.placeholder,
    value: modalSearch.value,
    top: modalSearch.getBoundingClientRect().top
  };
})()
