//called on document ready
$(function () {
  $('input[type="radio"]').on('click', function() {highlightChange()});
});


highlightChange = function () {
  $('input[type="radio"]').parent().removeClass();
  $(event.target).parent().addClass(event.target.value);
  //$('#personal_info').removeClass();
  //$('#personal_info').addClass(event.target.value);
}
