function addParagraphs(e) {
  var e = window.event;
  var target = e.target;
  var iden = target.id;
  var k = iden.slice(-1);
  var val = Number(k) + 1;

  document.getElementById('b' + k).style.display = 'none';
  var p2 =
    '<hr><div class="container" id="c' +
    val +
    '"><div class="col-lg-12 well"><div class="row"><form><div class="col-sm-12"><div class="row"><div class="form-group"><label>Project Title</label><input type="text" class="form-control"></div><div class="form-group" id="p' +
    val +
    '" class="collapse"><label>Description</label><textarea placeholder="Enter Project Description Here.." rows="3" class="form-control"></textarea></div></form></div></div><input type="button"  data-toggle="collapse" data-target="#p' +
    val +
    '" value="><"/><input id="b' +
    val +
    '" type="button" onclick="addParagraphs()" value="Add New Project" />';
  document.getElementById('c' + k).insertAdjacentHTML('afterend', p2);
}

$(document).ready(function() {
  $('#id_new_project_form').submit(function() {
    $('#id_error').text('');

    var frm = $('#id_new_project_form');
    var projectTitle = $('#id_new_project_title').val();
    var projectDescription = $('#id_new_project_description').val();

    var data = JSON.stringify({
      project_title: projectTitle,
      project_description: projectDescription,
    });

    $.ajax({
      type: frm.attr('method'),
      url: frm.attr('action'),
      contentType: 'application/json',
      data: data,
      success: function(result) {
        if (result.success === 1) {
          $('#id_error').text(result.message);
          $(location).attr('href', './projects');
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
