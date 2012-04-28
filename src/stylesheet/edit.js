$(document).ready(function(){
  //Hove effect when mouseover on ‰øÆÊîπ
	$('.anchorLink').hover(
	   function(e){
		   $('#edit').css("display", "block"); //show up #edit div when mouse cover
	   },
	   function(){
	 	   $('#edit').css("display", "none"); //hide #edit div when mouse leave
	   }
	);
	
	// Unbind hover,mouserenter,mouseleave.
	// Otherwise,User can't move away mouse from .anchorLink(aka:‰øÆÊîπÁöÑlink)
	$('.anchorLink').click(function(){
	  $(".anchorLink").unbind("hover").unbind('mouseenter').unbind('mouseleave');
	}); //http://api.jquery.com/hover/ see discussion from Zlatev replied to Thomas Svensson 
	
	// Jeditable for edit page. 
	$('.edit_default').editable('/edit',{
		indicator : '<img src="/image/loading.gif">',
		tooltip   : '點我修改吧',
		type      : "charcounter",
    select : true,
		submit: '改好了',
		cancel: '算了不改',
		rows: 5,
		cols: 25,
		charcounter: {characters: 360}
	});
	
  $('.edit_default').hover(
     function(e){
       $(this).css("background-color", "#CCFF66");
     },
     function(){
       $(this).css("background-color", "transparent");
		 }
	);	
}); //document.ready