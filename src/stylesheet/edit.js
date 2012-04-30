/*
 * We rely on two jquery plug-in to make edit.js works property. 
 * http://www.appelsiini.net/projects/jeditable for editing .
 * http://www.tomdeater.com/jquery/character_counter/ for character counting.
 * We import them from index.html 
 *    <script src="stylesheet/jeditable.js">
 *    <script src="stylesheet/jeditable.charcounter.js">
 */
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
	
	
	$.editable.addInputType('charcounter', {
	    element : function(settings, original) {
	        var textarea = $('<textarea />');
	        if (settings.rows) {
	            textarea.attr('rows', settings.rows);
	        } else {
	            textarea.height(settings.height);
	        }
	        if (settings.cols) {
	            textarea.attr('cols', settings.cols);
	        } else {
	            textarea.width(settings.width);
	        }
	        $(this).append(textarea);
	        return(textarea);
	    },
	    plugin : function(settings, original) {
	        $('textarea', this).charCounter(settings.charcounter.characters, settings.charcounter);
	    }
	});
	
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