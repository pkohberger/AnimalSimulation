$(document).ready(function() {

	$(window).unload(function () { 
		
		$(window).unbind('unload'); 

	});

    $('body, .page').css({height: $(window).height()});

	$(".loading").hide();

	$("#submit").click(function(){

		$(".loading").show();

	});

});