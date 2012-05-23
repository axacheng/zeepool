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
          dataType:"html",
          success: function(server_return) {
              // If server is no result back to client then show error mesg.
        	  //alert(server_return.length)
              if (server_return.length <= 2){
                $('.show_result_ok').hide()
                $('.show_result_error').fadeIn().delay(1000).fadeOut()
                return false
              }
        
              // Show content of search_result.html to #result div
        	  $('#result').html(server_return)

        	  // Search input from user:
        	  search_input = $('input#search_input').val()
        	  
        	  // Add next page link
        	  for (i=1; i< total_page; i++){
      	      //$('.navigation').append("<a href=/search/2	" + i + ">" +  "next page?" +  "</a>")
        	      $('.navigation').append("<a href=/search/2?term=m> next page </a>")        	    		  
        	  }
          }, //sucess end
        }) // $.ajax end
        
        
        	  


        // Clean up/Remove result after search is completed.
        // CANNOT REMOVE OUT!
        $('.show_line').empty().remove();
        $('.search_result').empty().remove();

  		}//source
  	}); //.autocomplete

	
	  // Infinite Scroll
	  var $container = $('.search_result');
	  $container.infinitescroll({
		  loading: {
		    finishedMsg: '沒有更多的字了',
		    msgText: '正在載入更多的字中～',
		    selector: null,
		    speed: 'slow',
		  },
		  state: { currPage: 1 },
		  binder: $(window), // used to cache the selector
		  nextSelector: "div.navigation a:first",
		  navSelector:  "div.navigation",
		  itemSelector: "div.post",
		  debug: true,
		  extraScrollPx: 350,
		  animate      : true,
		  dataType: 'html',
		  appendCallback: true,
		  bufferPx: 40,
		  infid: 0, //Instance ID
	  },
	  
	  // Masonry with InitifeScroll setting.
	  function(newElements) {
	    var $newElems = $(newElements).css({ opacity:0 });
	    $newElems.imagesLoaded(function(){
	    	$newElems.animate({ opacity:1 });        		    	
	    }) // imagesLoaded end
	  } //newElements end
	  ); // infinitescroll end
	  
  }); // search function end
