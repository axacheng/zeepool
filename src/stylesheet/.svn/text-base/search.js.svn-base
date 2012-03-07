/*
DO NOT USE IT! THIS FILE HAS BEEN DEPRECATED!
I USE autocom.js INSTEAD SEARCH FUNCTION.
*/

/*
$(document).ready(function(){
	$('.show_result_error').hide()
	$('.show_result_ok').hide()
	
	$("#search_button").click(function(){
		// Avoid blank string send to server
    var search_input = $('input#search_input').val();
    if (search_input == ""){
      $("input#search_input").focus();
    return false;}
		
		// Clean up/Remove result after search is completed.
		// CANNOT REMOVE OUT!
		$('.show_line').empty() 

    var inputString = 'q=' + $('#search_input').val()
    $.ajax({
			url: "/search?",
			type: "GET",
			data: inputString,
			dataType:"json",
			contentType: "application/json; charset=utf-8", 
			success: function(server_return){
				// If server is no result back to client then show error mesg.
				if (server_return.length == 0){
					$('.show_result_ok').hide()
				  $('.show_result_error').fadeIn().delay(2000).fadeOut()
					return false
				}
				else {
				  // (TODO) Instead of using (server_return.length) I actually can 
					// compute server_return object its length without hitting TotalWords   
          var key = server_return.length - 1 // decrement 1, because the first element starts as "Zero"
          var total_words = server_return[key].TotalWords
					$('.show_result_ok').html('<p class="show_result_ok">一共找到 ' + total_words + '字</p>').show()
				}

				// Loopup json result from server_return variable then compile them into html format.
        $.each(server_return, function(key) {
					$('#result').append(
					   '<p class="show_line">字：'  + server_return[key].Word + '</p>' +
             '<p class="show_line">解釋：' + server_return[key].Define + '</p>' +
             '<p class="show_line">例句：' + server_return[key].Example + '</p>'
					)
					   //$('#search_input').val('');
				}); //each end
			}, //sucess end
	   }); // $.ajax end
		return false; //force .submit malfunction
	}) // .click end
}); // document end
*/