$(document).ready(function() {
  alert('fdsa');
  $('#id_basic_details_form').submit(function() {
    $('#id_error').text('');

    var frm = $('#id_basic_details_form');
    var rollNo = $('#id_roll_no').val();
    var firstName = $('#id_first_name').val();
    var lastName = $('#id_last_name').val();
    var gender = $('#id_gender').val();
    var dateOfBirth = $('#id_date_of_birth').val();
    var email = $('#id_email').val();
    var phoneNumber = $('#id_phone_number').val();
    var address = $('#id_address').val();
    var medicalHistory = $('#id_medical_history').val();

    console.log('fdsafsda');
    console.log(firstName);

    $.ajax({
      type: frm.attr('method'),
      url: frm.attr('action'),
      contentType: 'application/json',
      data: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        gender: gender,
        date_of_birth: dateOfBirth,
        email: email,
        phone_number: phoneNumber,
        address: address,
        medical_history: medicalHistory,
      }),
      success: function(result) {
        if (result.success === 1) {
          $('#id_error').text(result.message);
          $(location).attr('href', './family');
        } else if (result.success === -99) {
          clearLoginCookie();
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

function getCookie(cname) {
  var name = cname + '=';
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return '';
}

function clearLoginCookie() {
  document.cookie = 'token=; path=/';
  $(location).attr('href', '/');
}
