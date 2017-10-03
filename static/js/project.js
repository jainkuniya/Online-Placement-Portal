function addParagraphs(e) {
    var e = window.event;
    var target = e.target;
    var iden = target.id;
    var k = iden.slice(-1);
    var val = Number(k) + 1;
    
    document.getElementById("b"+k).style.display="none";     
    var p2 = '<hr><div class="container" id="c'+val+'"><div class="col-lg-12 well"><div class="row"><form><div class="col-sm-12"><div class="row"><div class="form-group"><label>Project Title</label><input type="text" class="form-control"></div><div class="form-group" id="p'+val+'" class="collapse"><label>Description</label><textarea placeholder="Enter Project Description Here.." rows="3" class="form-control"></textarea></div></form></div></div><input type="button"  data-toggle="collapse" data-target="#p'+val+'" value="><"/><input id="b'+val+'" type="button" onclick="addParagraphs()" value="Add New Project" />';
    document.getElementById("c"+(k)).insertAdjacentHTML('afterend', p2);
}