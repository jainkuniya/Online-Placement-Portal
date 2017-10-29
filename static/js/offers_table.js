function edit_row(no)
{
 document.getElementById("edit_button"+no).style.display="none";
 document.getElementById("save_button"+no).style.display="block";
	
 var roll=document.getElementById("roll_row"+no);
 var name=document.getElementById("name_row"+no);
 var position=document.getElementById("position_row"+no);
 var package=document.getElementById("package_row"+no);

 var roll_data=roll.innerHTML;
 var name_data=name.innerHTML;
 var position_data=position.innerHTML;
 var package_data=package.innerHTML;

 roll.innerHTML="<input type='text' id='roll_text"+no+"' value='"+roll_data+"'>";
 name.innerHTML="<input type='text' id='name_text"+no+"' value='"+name_data+"'>";
 position.innerHTML="<input type='text' id='position_text"+no+"' value='"+position_data+"'>";
 package.innerHTML="<input type='text' id='package_text"+no+"' value='"+package_data+"'>";

}

function save_row(no)
{
 var roll_val=document.getElementById("roll_text"+no).value;
 var name_val=document.getElementById("name_text"+no).value;
 var position_val=document.getElementById("position_text"+no).value;
 var package_val=document.getElementById("package_text"+no).value;


 document.getElementById("roll_row"+no).innerHTML=roll_val;
 document.getElementById("name_row"+no).innerHTML=name_val;
 document.getElementById("position_row"+no).innerHTML=position_val;
 document.getElementById("package_row"+no).innerHTML=package_val;
 
 document.getElementById("edit_button"+no).style.display="block";
 document.getElementById("save_button"+no).style.display="none";
}

function delete_row(no)
{
 document.getElementById("row"+no+"").outerHTML="";
}

function add_row()
{
 var new_roll=document.getElementById("new_roll").value;
 var new_name=document.getElementById("new_name").value;
 var new_position=document.getElementById("new_position").value;
 var new_package=document.getElementById("new_package").value;
	
 var table=document.getElementById("data_table");
 var table_len=(table.rows.length)-1;
 var row = table.insertRow(table_len).outerHTML="<tr id='row"+table_len+"'><td id='roll_row"+table_len+"'>"+new_roll+"</td><td id='name_row"+table_len+"'>"+new_name+"</td><td id='position_row"+table_len+"'>"+new_position+"</td><td id='package_row"+table_len+"'>"+new_package+"</td><td><input type='button' id='edit_button"+table_len+"' value='Edit' class='edit btn btn-info' onclick='edit_row("+table_len+")'> <input type='button' id='save_button"+table_len+"' value='Save' class='save btn btn-primary' onclick='save_row("+table_len+")'> <input type='button' value='Delete' class='delete btn btn-danger' onclick='delete_row("+table_len+")'></td></tr>";


 document.getElementById("new_roll").value="";
 document.getElementById("new_name").value="";
 document.getElementById("new_position").value="";
 document.getElementById("new_package").value="";
}