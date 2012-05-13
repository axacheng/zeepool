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
  
  /*
   *  Like and Dislike incremental.
   *  When use click Like or DisLike on each Word <span> we'd increment value
   *  by one, afterward it'd send lose force and blur on the Like or Dislike.
   */
  

  $("a[name='like']").live({
	  click:function(){
		  var new_like_count = $("a[name='like_count']").text();
		  new_like_count = parseInt(new_like_count, 10);  //Use 10 as an radix.Dont change it!
		  $("a[name='like_count']").text(++new_like_count);	 
		  $("a[name='like']").die("click").css("color","#C0C0C0").remove();
	  } // end click
  }) //end live

  
  /*
   * Poll system, We use .live() event handler because search result gets 
   * dynamically generated by $('#result').append(). Base on tradition jquery selector
   * can not select 'freshest' DOM, so we have to use .live() after click event
   * gets triggered to select '.pollword' in <a>.
   * http://api.jquery.com/live/
   * 
   * We use $.ajax with GET method to /pollword/(.*)/(.*)
   * The first (.*) is pollword_choose. [like or dislike]
   * The second(.*) is pollword_key, which is 'name
   * 
   * e.g.: http://localhost:8080/pollword/like/azgduxmDmHd
   */ 

	$(".pollword").live({
		click:function(){
		  	var pollword_name = $(this).attr('id')
		  	var pollword_choose = $(this).attr('name')

		  	$.ajax({
				url: '/pollword/' + pollword_choose + '/' + pollword_name,
				type: "GET",
				dataType: "json",
				contentType: "application/json; charset=utf-8",
				success: function(response){
					//alert(response.total_count)
				},
				error: function(response){
					alert('DB error')  // (TODO): Need to change description.
				}
			}); //.ajax
		}  //poll .click end
	}) //live end
	
	
}); // document end

/* Search function 
 * jqueryUI autocomplete cannot included in $(document).ready!
 */
$(function(){
	$('#search_input').autocomplete({
    minLength: 1,
		source: function(inputString, server_return){
        $.ajax({
          url: "/search/?",
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
            var key = server_return.length - 1 // decrement 1, because the first element starts as "Zero"
            var total_words = server_return.length
            var searched_word = $('input#search_input').val()
            $('.show_result_ok').html('<p class="show_result_ok">我們有 ' + total_words + ' 個關於 ' +  searched_word + '的解釋').show()
          }
     
        // Loopup json result from server_return variable then compile them into html format.
        $.each(server_return, function(key) {
        	//alert(server_return[key].key)
          $('#result').append(
            '<tr>'+
            	'<td></td>'+
            	'<td class="search_result">'+
                  '<div class="show_line">字: '  + server_return[key].Word + '    ' +
                  '<span>'+
                      '<b><a name="like_count">' + server_return[key].Like +  '</a></b>  讚,' +
                      '<b><a name="dislike_count">' + server_return[key].Dislike + '</a></b> 不喜歡 ' +
                      '<a name="like" class="pollword" href="#" id=' + server_return[key].key + '>Like</a>  ' +
                      '<a name="dislike" class="pollword" href="#" id=' + server_return[key].key + '>Dislike</a>'+
                  '</span>' +
                  '</div>'+
                  '<div class="show_line">解釋: ' + server_return[key].Define +'</div>'+
                  '<div class="show_line">例句: ' + server_return[key].Example +'</div>'+
 			      '<div class="show_line">建立者: ' + server_return[key].Creator +'</div>'+
 			      '<div>'+
 	   			     '<span>'+ '建立時間: '+ server_return[key].Created + '</span>'+
 	   			    '<a href="http://www.facebook.com/sharer.php" name="fb_share" type="button_count">' + ' 分享到Facebook' + '</a>' +
 	              '</div>'+
            	'</td>'+
            '</tr>'
          ) // append end
        })//each end
        }, //sucess end
        }) // $.ajax end

        
        
      // Clean up/Remove result after search is completed.
      // CANNOT REMOVE OUT!
      $('.show_line').empty().remove();
      $('.search_result').empty().remove();   

		}//source
	}); //.autocomplete
}); // search function end<'