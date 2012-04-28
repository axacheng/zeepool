$(document).ready(function(){
	//data[0] return, check http://zeepooling.appspot.com/openid
	   $.getJSON("/auth_handler", function(data){
		 	$.each(data, function(k, v){
				$('.login_auth').append(
				   "<span>" + "<a href=\"" + v.url + "\">" + "<img src=\"" + v.image + "\">" + "</span>"
				)
			}) // each end
		 }); //.getJSON end	
}); // document end