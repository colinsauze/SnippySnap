display = (function () {
	
	addHandlers = function () {
		
		$('#search_field').on('change', function() {
			var value;
			value = $(this)[0].value;
			$('#search_text').attr('name', value);
		});
		
		$('#page_select').on('change', function () {
			window.location = window.location.toString().split('?')[0] + $(this)[0].value;
		});
		
		$('#page_size_select').on('change', function () {
			window.location = window.location.toString().split('?')[0] + $(this)[0].value;
		});
		
		$('.buttonlink').on('click', function(event){
		    event.preventDefault();
		    window.location = $(this).attr('data-url');
		});
	};

	return {addHandlers: addHandlers}
	
} () );