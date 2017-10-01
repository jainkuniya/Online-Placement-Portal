$(document).ready(function() {
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
      data: {
        rollNo: rollNo,
      },
      dataType: 'json',
      success: function(data) {
        if (data.success === 1) {
        } else if (data.success === -99) {
          clearLoginCookie();
        } else {
          $('#id_error_roll_no_form').text(data.message);
        }
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
        alert('Status: ' + textStatus);
        alert('Error: ' + errorThrown);
      },
    });
    return false;
  });
});
