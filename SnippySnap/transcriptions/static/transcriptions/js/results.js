results = (function () {
	
	addHandlers = function () {

		$('#page_select').on('change', function () {
			window.location = window.location.toString().split('?')[0] + $(this)[0].value
		});
		
	}
	return {addHandlers: addHandlers}
	
} () );