// Helper: update ranking system formula in raw editor textarea
const expr = `(function() {
  var ta = document.querySelector('textarea');
  var v = ta.value;
  v = v.replace('AIFactor(', 'AIFactorValidation(');
  v = v.replace('lgbm_slow2_backtest', 'lightgbm slow 2');
  var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  nativeSetter.call(ta, v);
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  return ta.value;
})()`;

process.stdout.write(expr);
