$(document).ready(function() {
  $('#password_form').invisible();
  $('.form')
    .find('input, textarea')
    .on('keyup blur focus', function(e) {
      var $this = $(this),
        label = $this.prev('label');

      if (e.type === 'keyup') {
        if ($this.val() === '') {
          label.removeClass('active highlight');
        } else {
          label.addClass('active highlight');
        }
      } else if (e.type === 'blur') {
        if ($this.val() === '') {
          label.removeClass('active highlight');
        } else {
          label.removeClass('highlight');
        }
      } else if (e.type === 'focus') {
        if ($this.val() === '') {
          label.removeClass('highlight');
        } else if ($this.val() !== '') {
          label.addClass('highlight');
        }
      }
    });

  $('.tab a').on('click', function(e) {
    e.preventDefault();

    $(this)
      .parent()
      .addClass('active');
    $(this)
      .parent()
      .siblings()
      .removeClass('active');

    target = $(this).attr('href');

    $('.tab-content > div')
      .not(target)
      .hide();

    $(target).fadeIn(600);
  });

  $('#roll_no_form').submit(function() {
    $('#id_error_roll_no_form').text('');

    var frm = $('#roll_no_form');
    var rollNo = $('#id_roll_no').val();

    $.ajax({
      type: frm.attr('method'),
      url: frm.attr('action'),
      contentType: 'application/json',
      data: JSON.stringify({
        rollNo: rollNo,
      }),
      success: function(result) {
        if (result.success === 1) {
          $('#id_roll_no_form_submit_button').invisible();
          $('#password_form').visible();

          var student = result.data.student;

          $('#id_first_name').val(student.first_name);
          $('#id_last_name').val(student.last_name);

          $('#id_label_first_name').addClass('active highlight');
          $('#id_label_last_name').addClass('active highlight');

          $('#id_roll_no').attr('disabled', 'disabled');
          $('#id_first_name').attr('disabled', 'disabled');
          $('#id_last_name').attr('disabled', 'disabled');
        } else if (result.success === -99) {
          clearLoginCookie();
        } else {
          $('#id_error_roll_no_form').text(result.message);
        }
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
        $('#id_error_roll_no_form').text('Error: ' + errorThrown);
      },
    });
    return false;
  });

  $('#password_form').submit(function() {
    $('#id_error_password_form').text('');

    var frm = $('#password_form');
    var rollNo = $('#id_roll_no').val();
    var password = $('#id_password').val();
    $.ajax({
      type: frm.attr('method'),
      url: frm.attr('action'),
      contentType: 'application/json',
      data: JSON.stringify({
        rollNo: rollNo,
        password: password,
      }),
      success: function(result) {
        if (result.success === 1) {
          '#id_error_password_form'.text('success');
        } else if (result.success === -99) {
          clearLoginCookie();
        } else {
          $('#id_error_password_form').text(result.message);
        }
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
        $('#id_error_password_form').text('Error: ' + errorThrown);
      },
    });
    return false;
  });
});

(function($) {
  $.fn.invisible = function() {
    return this.each(function() {
      $(this).css('visibility', 'hidden');
      $(this).css('height', 0);
    });
  };
  $.fn.visible = function() {
    return this.each(function() {
      $(this).css('visibility', 'visible');
      $(this).css('height', 'auto');
    });
  };
})(jQuery);
