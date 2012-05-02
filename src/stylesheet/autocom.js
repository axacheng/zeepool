$(document).ready(function(){
  $('.show_result_error').hide()
  $('.show_result_ok').hide()
  
	// Avoid blank string send to server
  $("#search_button").click(function(){
    var search_input = $('input#search_input').val();
    if (search_input == ""){
      $("input#search_input").focus();
    return false;}
	})
	
  // Prevent empty submit by pressing Enter key.
	$("#search_input").bind("keypress", function(v){
    if (v.keyCode == 13) //13 is Enter keycode
		  return false; 
  });
	
	// Watermark on search input
	var watermark = "點我找字";
  if ($("#search_input").val() == ""){
    $("#search_input").val(watermark).css("color", "#C0C0C0");
  }
  $("#search_input").focus(function(){
    if (this.value == watermark){
      this.value = ""; 
			$(this).css("color", "black")
    }
  }).blur(function() {
    if (this.value == "") {
      this.value = watermark;
			$(this).css("color", "#C0C0C0")
    }
  });
}); // document end

/*	poll function
 * 
 * 
 */



/* Search function 
 * jqueryUI autocomplete cannot included in $(document).ready!
 */
$(function(){
	$('#search_input').autocomplete({
    minLength: 1,
		source: function(inputString, server_return){
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
            $('.show_result_ok').html('<p class="show_result_ok">一共找到 ' + total_words + '字').show()
          }
        // Loopup json result from server_return variable then compile them into html format.
        $.each(server_return, function(key) {
        	for (i in server_return[0]) {
            	//alert(i)
        	}
          $('#result').append(
             '<div class="search_result">'+
               '<p class="show_line">字: '  + server_return[key].Word +
               '<span>'+
                 '<a href="#" class="pollword" value="1" return false>Like</a>' +
                 '<a href="#" class="pollword" value="1" return false>Dislike</a>'+
               '</span>' +
               '</p>'+
               '<p class="show_line">解釋: ' + server_return[key].Define +'</p>'+
               '<p class="show_line">例句: ' + server_return[key].Example +'</p>'+
			   '<p class="show_line">建立者: ' + server_return[key].Creator +'</p>'+
			   '建立時間: '+ server_return[key].Updated['ctime'] +
			   '<a href="http://www.facebook.com/sharer.php" name="fb_share" type="button_count">' + ' 分享到Facebook' + '</a>' +
             '</div>' 
          )
        })//each end
        }, //sucess end
        }) // $.ajax end
        
      // Clean up/Remove result after search is completed.
      // CANNOT REMOVE OUT!
      $('.show_line').empty().remove();
      $('.search_result').empty().remove();   

		}//source
	}); //.autocomplete
}); // document end