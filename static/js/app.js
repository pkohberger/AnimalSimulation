$(document).ready(function() {

    $('body, .page').css({height: $(window).height()});

	$(".loading").hide();

	$("#submit").click(function(){

		$(".loading").show();

	});

});