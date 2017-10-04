$(document).ready(function() {
  // alert('fdasa');
  $('#id_new_exprience_form').submit(function() {
    $('#id_error').text('');

    var frm = $('#id_new_exprience_form');

    var data = JSON.stringify({
      exprience_responsibility: $('#id_new_exprience_responsibility').val(),
      exprience_work: $('#id_new_exprience_work').val(),
      exprience_company: $('#id_new_exprience_company').val(),
    });

    // alert(data);

    $.ajax({
      type: frm.attr('method'),
      url: frm.attr('action'),
      contentType: 'application/json',
      data: data,
      success: function(result) {
        if (result.success === 1) {
          $('#id_error').text(result.message);
          $(location).attr('href', './exprience');
        } else if (result.success === -99) {
          $(location).attr('href', './logout');
        } else {
          $('#id_error').text(result.message);
        }
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
        $('#id_error').text('Error: ' + errorThrown);
      },
    });
    return false;
  });
});

function toggleState(id) {
  var element = document.getElementById(id),
    style = window.getComputedStyle(element),
    visibility = style.getPropertyValue('visibility');
  if (visibility === 'hidden') {
    element.style.visibility = 'visible';
    element.style.height = 'auto';
  } else {
    element.style.visibility = 'hidden';
    element.style.height = 0;
  }
}
