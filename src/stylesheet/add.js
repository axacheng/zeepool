$(document).ready(function(){
	//First hide form on add_form, when user clicking 'Add' it will show up
	$(".toggle").click(function(){
    $.blockUI({ message: $('#add_main'),
		            css: { width: '50%',
						   top: '20%',
						   left: '30%',
						   cursor: 'wait', },
						   overlayCSS:  { 
							   backgroundColor: '#000', 
							   opacity:0.75 },					
	}); // .blockUI end
    
	$('.blockOverlay').attr('title','點我離開取消編輯').click($.unblockUI);
    //reset all form fields each time when user clicking.
		$("form").each(function(){
      this.reset();
    });
  }) // toggle end

	  $('#add_form').submit(function(){
      var form = $(this),
      formData = form.serialize(),
      formMethod = form.attr('method'),
      responseText = $('#submit_result') 
      responseText.hide()
                  .addClass('waiting')
                  .text('等一下...儲存中')
                  .fadeIn(200);
    $.ajax({
        url: "/add",
        type: formMethod,
        data: formData,
        success: function(data){
          var responseData = $.parseJSON(data), responseData_class = '';
          switch(responseData.status){
            case 'error':
              responseData_class = 'response_error';
            break;
            case 'success':
              responseData_class = 'response_success';
            break;
            default:
                alert('Sorry, We dont get response from server while adding ' +
                	  'your word. Please try again later.')
          }
          
          responseText.fadeOut(200, function(){
            $(this).removeClass('waiting')
                   .addClass(responseData_class)
                   .text(responseData.message)
                   .fadeIn(200,function(){
                       setTimeout(function(){
                       responseText.fadeOut(200,function(){
                           $(this).removeClass(responseData_class);
                     });
                     }, 3000);
					  $.unblockUI(); //Remove block and back to normal
					  
						// Show all words we have after word successfully committed.
						// (TODO) It should be done by "really" page reload.
						// Now, it's just plus 1 on <span class=".all_words"> as fake ;)
					  var new_number = parseInt($('.all_words').text()) + 1
						new_all_words_as_text = new_number.toString()
						$('.all_words').text(new_all_words_as_text)
								
					         }); //fadeIn end
          }); //responseText.fadeOut
        } //$.ajax success
    });//$.ajax
    return false;
    }); //add_form submit
//	}) // IT WILL CAUSE THE DUPLICATE SUBMIT PROBLEM!!!! add_word toggle click
}); 