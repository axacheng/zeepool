/*
 * We rely on two jquery plug-in to make edit.js works property. 
 * http://www.appelsiini.net/projects/jeditable for editing .
 * http://www.tomdeater.com/jquery/character_counter/ for character counting.
 * We import them from index.html 
 *    <script src="stylesheet/jeditable.js">
 *    <script src="stylesheet/jeditable.charcounter.js">
 */


		
$(document).ready(function(){
	/*
	 * I emulated www.teamviget.com 3D rotate display by using css3 -webkit-transfrom
	 * rotate3d method to switch around #home div and #edit div.
	 */
	
    $("#edit_toggle").click(function(event){
			  setTimeout(function(){
					$("#home").css({"opacity":"0", "left":"-100%", "-webkit-transform":"rotate3d(0, 0, 0, -10deg)", "z-index":"2"});
					$("#edit").css({"opacity":"1", "left":"0px", "-webkit-transform":"rotate3d(0, 0, 0, 0deg)", "z-index":"10"});
					location.hash = location.hash.replace("#", "#!");
			  }, 10);

		  } // end click
	  ); //end live

	/*
    $("#edit_toggle").click(function(event){
		$("#home").css({"opacity":"0", "left":"-100%", "-webkit-transform":"rotate3d(0, 0, 0, -10deg)", "z-index":"2"});
		$("#edit").css({"opacity":"1", "left":"0px", "-webkit-transform":"rotate3d(0, 0, 0, 0deg)", "z-index":"10"});
    	var s = location.hash = "#!edit"
    	console.log(s);
    	
		//var c = s.replace("#", "#!");

		
		//location.hash = location.hash.replace("#", "#!");
		//console.log(location.hash);
    }); // #edit_toggle.click end
    */

    $("#edit_finish").click(function(event){
			  setTimeout(function(){
					$("#edit").css({"opacity":"0", "left":"-100%", "-webkit-transform":"rotate3d(0, 0, 0, -10deg)", "z-index":"2"});
					$("#home").css({"opacity":"1", "left":"0px", "-webkit-transform":"rotate3d(0, 0, 0, 0deg)", "z-index":"10"});
					location.hash = location.hash.replace("#", "#!");
			  }, 10);

		  } // end click
	  ); //end live	  

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